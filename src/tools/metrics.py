from dataclasses import dataclass
from enum import Enum

from core.simulated_annealing import Response
from algorithm.smt_state import SMTState

from entities.smt_entities import OP

@dataclass(frozen=True)
class StateStatistic:
    energy: float
    setup_transition_time: float

@dataclass(frozen=True)
class ComparisonStatistics:
    name: str
    historical: StateStatistic
    optimized: StateStatistic
    gain: float

class RequiredTime(float, Enum):
    SOLDER_PASTE = 10.0
    PAINEL = 10.0
    CONVEYOR = 5.0

def states_comparison(historical:SMTState, optimized:SMTState, name:str = "") -> ComparisonStatistics:
    return ComparisonStatistics(
        name=name,
        historical=StateStatistic(
            energy=historical.energy,
            setup_transition_time=get_setup_transition_time(historical)
        ),
        optimized=StateStatistic(
            energy=optimized.energy,
            setup_transition_time=get_setup_transition_time(optimized)
        ),
        gain=(optimized.energy - historical.energy)/historical.energy
    )

def get_setup_transition_time(state: SMTState) -> float:
    alloc = state.get_allocations()

    total_time = 0.0
    for line in alloc:
        for i in range(len(line.products) - 1):
            from_op = line.products[i]
            to_op = line.products[i + 1]
            setup_transition_time = (
                from_op.oven_transition_costs.get(to_op.temperature_profile_code, 0.0)
                + _get_paste_transition_cost(from_op.solder_paste_id, to_op.solder_paste_id)
                + _get_painel_transition_cost(from_op.painel_id, to_op.painel_id)
                + _get_conveyor_transition_cost(from_op.conveyor_id, to_op.conveyor_id)
            )
            total_time += setup_transition_time

    return total_time


def _get_paste_transition_cost(code_from: int, code_to: int) -> float:
    """Retorna o custo de transição entre pastas de solda. Custo fixo se forem diferentes, zero se iguais."""
    return RequiredTime.SOLDER_PASTE.value if code_from != code_to else 0.0

def _get_painel_transition_cost(code_from: int, code_to: int) -> float:
    """Retorna o custo de transição entre painéis. Custo fixo se forem diferentes, zero se iguais."""
    return RequiredTime.PAINEL.value if code_from != code_to else 0.0

def _get_conveyor_transition_cost(code_from: int, code_to: int) -> float:
    """Retorna o custo de transição entre conveyors. Custo fixo se forem diferentes, zero se iguais."""
    return RequiredTime.CONVEYOR.value if code_from != code_to else 0.0

def calcular_limite_inferior_teorico(ops: list[OP], num_linhas: int = 2) -> float:
    """
    Calcula o Limite Inferior Teórico (Lower Bound) relaxando todas as restrições 
    de setup e assumindo um balanceamento perfeito entre as linhas.
    """
    tempo_total_ideal = 0.0
    
    for op in ops:
        if op.total_time:
            melhor_tempo_op = min(op.total_time.values())
            tempo_total_ideal += melhor_tempo_op
    limite_inferior = tempo_total_ideal
    
    return limite_inferior

