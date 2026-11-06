from entities.smt_entities import OP
from entities.penalty import Penalty

class TransitionTools:
    """
    Utilitário responsável pelo cálculo dos custos de transição de setup.
    Isolado para reduzir o acoplamento no SMTState e otimizar a performance.
    """
    def __init__(self, penalty: Penalty):
        self._penalty = penalty

    def calculate_transition_cost(self, current_op: OP, next_op: OP) -> float:
        """
        Calcula o custo total de setup entre duas OPs consecutivas de forma otimizada.
        As validações são feitas inline para evitar o overhead de múltiplas chamadas
        de método durante as iterações do Simulated Annealing.
        """
        cost = 0.0
        p = self._penalty

        # 1. Troca de Pasta de Solda
        if current_op.solder_paste_id != next_op.solder_paste_id:
            cost += p.PASTE_PENALTY
            
        # 2. Troca de Família de Painel
        if current_op.painel_id != next_op.painel_id:
            cost += p.PANEL_PENALTY
            
        # 3. Ajuste de Largura da Esteira (Conveyor)
        if current_op.width != next_op.width:
            cost += p.CONVEYOR_PENALTY
            
        # 4. Troca de Tipo de Forno (Perfil de Temperatura)
        if current_op.temperature_profile_code != next_op.temperature_profile_code:
            cost += p.TYPE_OVEN_PENALTY

        # 5. Custo específico de transição do forno oriundo da OP
        # O type: ignore é mantido conforme sua implementação original
        oven_cost = current_op.get_oven_transition_cost(next_op.temperature_profile_code) # type: ignore
        cost += oven_cost
        
        return cost