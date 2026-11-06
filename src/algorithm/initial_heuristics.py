import random

from entities.smt_entities import OP, LineAllocation
from algorithm.transition_tools import TransitionTools


def init_line_state(allocations: list[LineAllocation]) -> "tuple[dict[int, float], dict[int, OP | None]]":
    workloads: dict[int, float] = {}
    last_ops: dict[int, OP | None] = {}

    for line in allocations:
        all_line_ops = line.pinned_products + line.products
        workloads[line.plan_line_id] = sum(
            op.total_time[line.plan_line_id]
            for op in all_line_ops
            if line.plan_line_id in op.total_time
        )
        last_ops[line.plan_line_id] = all_line_ops[-1] if all_line_ops else None

    return workloads, last_ops


def select_op_for_line(
    line_id: int,
    slack: float,
    remaining_ops: list[OP],
    last_op: "OP | None",
    transition_tools: TransitionTools
) -> "OP | None":
    valid_candidates = [
        op for op in remaining_ops
        if line_id in op.total_time and op.total_time[line_id] < slack
    ]
    
    if not valid_candidates:
        return None
        
    if last_op is None:
        return valid_candidates[0]  # noqa: S311
    
    return min(
        valid_candidates,
        key=lambda op: transition_tools.calculate_transition_cost(last_op, op),
    )


def greedy_initial_allocation(
    allocations: list[LineAllocation], 
    unallocated_ops: list[OP],
    transition_tools: TransitionTools,
    reserved_id: int
) -> LineAllocation:
    if not unallocated_ops:
        return LineAllocation(reserved_id, [])

    remaining_ops = unallocated_ops[:]
    workloads, last_ops = init_line_state(allocations)

    while remaining_ops:
        sorted_lines = sorted(allocations, key=lambda l: workloads[l.plan_line_id])
        allocated_in_this_round = False

        for target_line in sorted_lines:
            line_id = target_line.plan_line_id
            slack = target_line.availability - workloads[line_id]
            
            best_op = select_op_for_line(
                line_id, slack, remaining_ops, last_ops[line_id], transition_tools
            )

            if best_op is None:
                continue  

            target_line.products.append(best_op)
            remaining_ops.remove(best_op)

            workloads[line_id] += best_op.total_time[line_id]
            last_ops[line_id] = best_op
            allocated_in_this_round = True
            
            break

        if not allocated_in_this_round:
            break

    return LineAllocation(reserved_id, remaining_ops)
