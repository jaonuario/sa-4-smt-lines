import logging
from entities.historical_balancing import HistoricalBalancing
from exceptions.smt_invalid_data_error import SMTInvalidDataError
from repository.production_plan_repository import ProductionPlanRepository
from repository.product_setup_repository import ProductSetupRepository
from repository.product_rate_repository import ProductRateRepository
from repository.oven_transition_repository import OvenTransitionRepository
from algorithm.smt_state import SMTState
from entities.smt_entities import OP, LineAllocation

# Modo de taxas usado em TODA comparação histórico x otimizado (testers, teste.py,
# validacao.py). Ambos os estados (humano e otimizado) devem ser montados com o
# mesmo modo, senão a energia base do histórico não é comparável.
#   True  -> linhas sem taxa cadastrada herdam a maior taxa do produto (relaxado)
#   False -> apenas linhas com taxa cadastrada são compatíveis (restrição real)
HISTORICAL_FULL = True


class ScenarioBuilder:
    def __init__(self, num_lines: int = 3, full: bool = False):
        logging.info("[ScenarioBuilder] Carregando bases de dados em memória...")
        self.num_lines = num_lines
        
        self.setups = ProductSetupRepository().get_all()
        self.rates = ProductRateRepository().get_all_rates_full(num_lines=self.num_lines) if full else ProductRateRepository().get_all_rates()
        self.oven_transitions = OvenTransitionRepository().get_all()
        
        self._paste_to_id: dict[str, int] = {}
        self._painel_to_id: dict[str, int] = {}
        self._warned_products: set[int] = set()

    def _warn_dropped(self, plan_item_id: int, product_id: int, reason: str) -> None:
        """Avisa o descarte de um produto apenas uma vez por builder (load_basic roda por cenário)."""
        if product_id not in self._warned_products:
            self._warned_products.add(product_id)
            logging.warning(f"[ScenarioBuilder] OP {plan_item_id} descartada: {reason} (produto {product_id}).")

    def _get_mapped_id(self, mapping_dict: dict[str, int], key: str | int | None) -> int:
        """Garante que atributos de texto virem inteiros únicos para performance no SA."""
        if key is None or key == "":
            return 0  # 0 será nosso ID padrão para ausência de informação
            
        key_str = str(key).strip().upper()
        if key_str not in mapping_dict:
            mapping_dict[key_str] = len(mapping_dict) + 1
        return mapping_dict[key_str]

    def build_op(self, plan_item_id: int, product_id: int, quantity: int, priority: int, n_lines:list[int] | None = None) -> OP | None:
        """Fábrica central de OPs. Garante que OPs do histórico e do plano básico sejam idênticas estruturalmente."""
        setup = self.setups.get(product_id)
        if not setup:
            self._warn_dropped(plan_item_id, product_id, "setup ausente")
            return None

        product_rates = self.rates.get(product_id)
        if not product_rates:
            self._warn_dropped(plan_item_id, product_id, "taxas (rates) ausentes")
            return None

        total_time = {}
        for line_id, uph in product_rates.items():
            if uph > 0:
                # if n_lines is None or line_id in n_lines:                
                total_time[line_id] = quantity / uph
                
        if not total_time:
            self._warn_dropped(plan_item_id, product_id, "sem UPH > 0 em nenhuma linha")
            return None

        transitions_for_op = self.oven_transitions.get(setup.oven_profile, {})

        try:
            return OP(
            plan_item_id=plan_item_id,
            product_id=product_id,
            priority=priority,
            total_time=total_time, # Todas as linhas agora estão aqui!
            solder_paste_id=self._get_mapped_id(self._paste_to_id, setup.paste),
            painel_id=self._get_mapped_id(self._painel_to_id, setup.painel),
            width=setup.width or 0.0,
            temperature_profile_code=setup.oven_profile or "DEFAULT",
            oven_transition_costs=transitions_for_op
        )
        except SMTInvalidDataError as e:
            logging.warning(e)
            return None

    @staticmethod
    def _log_coverage(source: str, total: int, valid: int) -> None:
        """Resume quantas OPs da fonte foram efetivamente usadas no cenário."""
        dropped = total - valid
        if dropped:
            logging.warning(
                f"[ScenarioBuilder] '{source}': {valid}/{total} OPs utilizadas, "
                f"{dropped} descartadas ({dropped / total:.0%}) por dados incompletos."
            )
        else:
            logging.info(f"[ScenarioBuilder] '{source}': todas as {total} OPs utilizadas.")

    def load_basic(self, plan_filename: str = "production_plan.csv") -> tuple[list[LineAllocation], list[OP]]:
        """Gera o cenário para otimização do zero."""
        plan_items = ProductionPlanRepository().get(plan_filename)
        ops: list[OP] = []
        
        for item in plan_items:
            op = self.build_op(item.plan_id, item.product_id, item.quantity, item.priority)
            if op:
                ops.append(op)
                
        self._log_coverage(plan_filename, len(plan_items), len(ops))

        allocations = [
            LineAllocation(plan_line_id=i, availability=10080.0, products=[], pinned_products=[])
            for i in range(1, self.num_lines + 1)
        ]

        return allocations, ops

    def load_historical(self, historical: HistoricalBalancing, lock:bool = True) -> tuple[SMTState, SMTState]:
        """
        Gera dois estados: 
        1. O estado engessado (fiel ao histórico para extrairmos a Energia Base).
        2. O estado livre (mesmas OPs, mas não alocadas, para darmos ao otimizador).
        """
        historical_allocations: list[LineAllocation] = []
        empty_allocations: list[LineAllocation] = []
        non_allocation: list[OP] = []
        all_ops: list[OP] = []
        
        # CORREÇÃO 3: Gerador para garantir que cada Lote/OP tenha um ID único na simulação
        gerador_id_op = 90000
        total_lotes = 0

        for line_id in historical.line_ids:
            if line_id not in historical.line_allocations:
                raise ValueError(f"Line ID {line_id} ausente nas alocações.")
                
            hist_line = LineAllocation(plan_line_id=line_id, availability=10080.0, products=[], pinned_products=[])
            empty_line = LineAllocation(plan_line_id=line_id, availability=10080.0, products=[], pinned_products=[])
            
            # CORREÇÃO 2: Desempacotando a tupla (product_id, qty) da nova arquitetura
            for product_id, qty in historical.line_allocations[line_id]:
                gerador_id_op += 1
                total_lotes += 1

                # CORREÇÃO 1 e 3: Usamos o gerador como plan_item_id e REMOVEMOS lines=[line_id]
                op = self.build_op(
                    plan_item_id=gerador_id_op, 
                    product_id=product_id, 
                    quantity=qty, 
                    priority=1,
                    # nes=[line_id] if lock else []
                )
                
                if op:
                    # A validação do humano continua aqui. Se o humano alocou na máquina errada, penaliza.
                    if line_id not in op.total_time:
                        logging.warning(f"Histórico alocou produto {product_id} na linha {line_id}, mas ele é incompatível! Forçando aceite.")
                        non_allocation.append(op)
                    else:    
                        hist_line.products.append(op)
                        
                    all_ops.append(op)
                
            historical_allocations.append(hist_line)
            empty_allocations.append(empty_line)
            
        self._log_coverage(historical.name, total_lotes, len(all_ops))

        state_historico = SMTState(allocations=historical_allocations, product_orders=non_allocation, inicialization=False)
        state_vazio_para_otimizar = SMTState(allocations=empty_allocations, product_orders=all_ops)
        
        return state_historico, state_vazio_para_otimizar