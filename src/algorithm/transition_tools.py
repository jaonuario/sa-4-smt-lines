from entities.smt_entities import OP
from entities.penalty import Penalty

class TransitionTools:
    def __init__(self, penalty: Penalty):
        self._penalty = penalty

    def calculate_transition_cost(self, current_op: OP, next_op: OP) -> float:
        cost = 0.0
        p = self._penalty

        if current_op.solder_paste_id != next_op.solder_paste_id:
            cost += p.PASTE_PENALTY
            
        if current_op.painel_id != next_op.painel_id:
            cost += p.PANEL_PENALTY
            
        if current_op.width != next_op.width:
            cost += p.CONVEYOR_PENALTY
            
        if current_op.temperature_profile_code != next_op.temperature_profile_code:
            cost += p.TYPE_OVEN_PENALTY

        oven_cost = current_op.get_oven_transition_cost(next_op.temperature_profile_code) # type: ignore
        cost += oven_cost
        
        return cost
