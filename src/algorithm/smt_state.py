import random
import math

from exceptions.smt_invalid_data_error import SMTInvalidDataError
from core.simulated_annealing import State
from algorithm.transition_tools import TransitionTools
from algorithm.initial_heuristics import greedy_initial_allocation
from entities.smt_entities import OP, LineAllocation
from entities.penalty import Penalty


class SMTState(State):
    RESERVED_ID = -1
    
    def __init__(
        self,
        allocations: list["LineAllocation"],
        product_orders: list[OP] | None = None,
        penalty: Penalty | None = None,
        transition_tools: TransitionTools | None = None,
        inicialization: bool = True
    ) -> None:
        
        for line in allocations: 
            if line.plan_line_id == self.RESERVED_ID:
                raise SMTInvalidDataError(
                    f"Linha utilizando identificador reservado {self.RESERVED_ID}"
                )  
                
        product_orders = product_orders or []
        
        self._allocations = allocations
        self._penalty = penalty or Penalty()
        self._transition_tools = transition_tools or TransitionTools(self._penalty)
        self._energy = None
        if inicialization:
            self._non_allocation = greedy_initial_allocation(
                allocations=self._allocations,
                unallocated_ops=product_orders,
                transition_tools=self._transition_tools,
                reserved_id=self.RESERVED_ID
            )
        else:
            self._non_allocation = LineAllocation(plan_line_id=self.RESERVED_ID, products=product_orders)
        
        all_ops = self.get_all_ops()
        self._max_priority = max((op.priority for op in all_ops), default=1)

    @property
    def energy(self) -> float:
        """Calcula o custo total da solução."""
        if self._energy is not None:
            return self._energy
        
        total_setup_cost = 0.0
        total_priority_penalty = 0.0
        total_availability_penalty = 0.0
        workloads: list[float] = []

        for line in self._allocations:
            line_setup_cost: float = 0.0
            line_proc_time = 0.0
            ops = line.pinned_products + line.products
            
            for i in range(len(ops)):
                op = ops[i]

                # 1. Hard Constraint: Incompatibilidade
                if line.plan_line_id not in op.total_time:
                    return self._penalty.INCOMPATIBILITY_PENALTY

                # 2. Tempo de Produção:
                line_proc_time += op.total_time[line.plan_line_id]

                # 3. Custo de Setup (Agora usando a TransitionTools)
                if i < len(ops) - 1:
                    next_op = ops[i + 1]
                    line_setup_cost += self._transition_tools.calculate_transition_cost(op, next_op)
            
            min_priority_seen_ahead = float('inf')
            num_pinned = len(line.pinned_products)
            for i in range(len(ops) - 1, num_pinned - 1, -1):
                op = ops[i]
                
                if op.priority > min_priority_seen_ahead:
                    delta_p = abs(op.priority - min_priority_seen_ahead)
                    total_priority_penalty += (self._penalty.PRIORITY_PENALTY * delta_p)
                    
                elif op.priority < min_priority_seen_ahead:
                    min_priority_seen_ahead = op.priority

            current_workload: float = line_proc_time + line_setup_cost
            # 5. Penalidade de Disponibilidade         
            if line.availability:
                delta = line.availability - current_workload
                
                if delta < 0:
                    overhead_ratio = abs(delta) / line.availability
                    if overhead_ratio > 0.1:
                        return self._penalty.INCOMPATIBILITY_PENALTY
                    else:
                        total_availability_penalty += (abs(delta) * self._penalty.OVER_AVAILABILITY_PENALTY) ** 2

            workloads.append(current_workload)
            total_setup_cost += line_setup_cost

        if not workloads:
            return self._penalty.INCOMPATIBILITY_PENALTY

        # 6. Penalidade de Balanceamento (Makespan)
        mean_workload = sum(workloads) / len(workloads)
        balance_penalty = math.sqrt(sum(((w - mean_workload) ** 2) / len(workloads) for w in workloads))

        self._energy = float(
            total_setup_cost
            + balance_penalty
            + total_priority_penalty
            + total_availability_penalty
            + self._get_non_alloc_workload()
        )

        return self._energy

    def next_state(self) -> "SMTState":
        """Gera um estado vizinho através de mutações estocásticas com garantia de alteração."""        
        new_allocations = [line.copy() for line in self._allocations]
        new_non_alloc = self._non_allocation.copy() if self._non_allocation else None
        
        all_lines = new_allocations[:]
        if new_non_alloc is not None:
            all_lines.append(new_non_alloc)

        mutated = False
        attempts = 0
        MAX_ATTEMPTS = 15

        # Pré-filtros executados uma única vez para evitar sorteios inúteis
        linhas_com_produtos = [l for l in all_lines if l.products]
        linhas_com_multiplos_produtos = [l for l in all_lines if len(l.products) >= 2]

        if not linhas_com_produtos or (len(linhas_com_produtos) == 1 and not linhas_com_multiplos_produtos and len(all_lines) == 1):
            return self._generate_new_state(new_alloc=new_allocations, new_non_alloc=new_non_alloc)

        # Loop de garantia: o SA não vai desperdiçar ciclos avaliando estados idênticos
        while not mutated and attempts < MAX_ATTEMPTS:
            movimento = random.choices(
                population=["inter_swap", "move", "intra_swap"], 
                weights=[0.3, 0.4, 0.3], 
                k=1
            )[0]

            if movimento == "inter_swap" and len(linhas_com_produtos) >= 2:
                l1, l2 = random.sample(linhas_com_produtos, 2)
                idx1 = random.randrange(len(l1.products))
                idx2 = random.randrange(len(l2.products))
                
                op1 = l1.products[idx1]
                op2 = l2.products[idx2]
                
                l1_suporta_op2 = (l1.plan_line_id in op2.total_time) or (l1.plan_line_id == self.RESERVED_ID)
                l2_suporta_op1 = (l2.plan_line_id in op1.total_time) or (l2.plan_line_id == self.RESERVED_ID)
                
                if l1_suporta_op2 and l2_suporta_op1:
                    l1.products[idx1], l2.products[idx2] = op2, op1
                    mutated = True
            
            elif movimento == "move" and linhas_com_produtos:
                l_orig = random.choice(linhas_com_produtos)
                op_idx = random.randrange(len(l_orig.products))
                op_candidata = l_orig.products[op_idx]
                
                # Hard Constraint: Destino deve suportar a OP
                destinos_validos = [
                    l for l in all_lines 
                    if l != l_orig and (l.plan_line_id in op_candidata.total_time or l.plan_line_id == self.RESERVED_ID)
                ]
                
                if destinos_validos:
                    l_dest = random.choice(destinos_validos)
                    op = l_orig.products.pop(op_idx)
                    l_dest.products.insert(random.randint(0, len(l_dest.products)), op)
                    
                    # Atualiza o filtro dinamicamente caso a linha de origem tenha esvaziado
                    if not l_orig.products:
                        linhas_com_produtos.remove(l_orig)
                        
                    mutated = True

            elif movimento == "intra_swap" and linhas_com_multiplos_produtos:
                # Sorteia direto de linhas que sabidamente têm 2 ou mais OPs
                l1 = random.choice(linhas_com_multiplos_produtos)
                idx1, idx2 = random.sample(range(len(l1.products)), 2)
                l1.products[idx1], l1.products[idx2] = l1.products[idx2], l1.products[idx1]
                mutated = True

            attempts += 1

        return self._generate_new_state(new_alloc=new_allocations, new_non_alloc=new_non_alloc)
     
    def get_allocations(self) -> list["LineAllocation"]:
        return self._allocations
    
    def get_non_allocations(self) -> LineAllocation:
        return self._non_allocation
    
    def get_all_ops(self) -> list[OP]:
        return [op for line in self._allocations for op in line.products + line.pinned_products] + self._non_allocation.products
    
    def _get_non_alloc_workload(self) -> float:
        workload = 0.0
        for product in self._non_allocation.products:
            times = list(product.total_time.values())
            if times:
                weight = float(self._max_priority - product.priority + 1)
                workload += weight * self._penalty.UNALLOCATED_OP_PENALTY
        return workload

    def _generate_new_state(self, new_alloc: list[LineAllocation], new_non_alloc: LineAllocation | None):
        new_state = SMTState.__new__(SMTState)
        new_state._allocations = new_alloc
        new_state._non_allocation = new_non_alloc
        new_state._energy = None
        new_state._penalty = self._penalty
        new_state._max_priority = self._max_priority
        new_state._transition_tools = self._transition_tools
        return new_state
