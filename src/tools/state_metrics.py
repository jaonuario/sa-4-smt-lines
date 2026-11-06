import math
from algorithm.smt_state import SMTState

class StateMetrics:
    def __init__(self, state: SMTState):
        self.state = state
        self.line_workloads: list[float] = []
        self.line_setups: list[float] = []
        
        self._extract_metrics()

    def _extract_metrics(self) -> None:
        allocations = self.state.get_allocations()
        
        for line in allocations:
            line_id = line.plan_line_id
            total_line_workload = 0.0
            total_line_setup = 0.0
            
            all_ops = line.pinned_products + line.products
            
            if not all_ops:
                self.line_workloads.append(0.0)
                self.line_setups.append(0.0)
                continue
                
            tools = self.state._transition_tools
            
            for i, op in enumerate(all_ops):
                total_line_workload += op.total_time.get(line_id, 0.0)
                
                if i > 0:
                    prev_op = all_ops[i - 1]
                    
                    setup_cost = tools.calculate_transition_cost(prev_op, op)
                    
                    total_line_setup += setup_cost
                    total_line_workload += setup_cost
                    
            self.line_workloads.append(total_line_workload)
            self.line_setups.append(total_line_setup)

    @property
    def total_energy(self) -> float:
        return self.state.energy

    @property
    def max_makespan(self) -> float:
        if not self.line_workloads:
            return 0.0
        return max(self.line_workloads)

    @property
    def load_imbalance(self) -> float:
        if not self.line_workloads:
            return 0.0
        mean = sum(self.line_workloads) / len(self.line_workloads)
        variance = sum((w - mean) ** 2 for w in self.line_workloads) / len(self.line_workloads)
        return math.sqrt(variance)

    @property
    def total_setup_cost(self) -> float:
        return sum(self.line_setups)

    @property
    def unallocated_penalty(self) -> float:
        return self.state._get_non_alloc_workload()
