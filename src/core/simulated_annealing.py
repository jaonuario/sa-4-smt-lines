from dataclasses import dataclass
import logging
import math
import random
import time
from abc import ABC, abstractmethod


class State(ABC):
    @property
    @abstractmethod
    def energy(self) -> float:
        return 0.0

    @abstractmethod
    def next_state(self) -> "State":
        return self


@dataclass(frozen=True)
class Response:
    initial_state: State
    best_state: State
    initial_energy: float
    best_energy: float
    iterations: int
    temperature: float
    high_temp: float
    freezing_temp: float
    freezing_coef: float
    energy_history: list[float]
    energy_accepted_history: list[float]
    execution_time: float

    def __repr__(self):
        return (f"Response(initial_energy={self.initial_energy:.4f}, best_energy={self.best_energy:.4f}, "
                f"iterations={self.iterations}, final_temperature={self.temperature:.4f})")


class SimulatedAnnealing:
    def __init__(
        self,
        high_temp: float = 1000.0,
        freezing_temp: float = 0.0001,
        freezing_coef: float = 0.9995,
        max_idle_time: int = 10000
    ):
        self._high_temp = high_temp
        self._freezing_temp = freezing_temp
        self._freezing_coef = freezing_coef
        self._max_idle_time = max_idle_time

    def run(self, initial_state: State, idle: bool = True) -> Response:
        temperature = self._high_temp
        
        current_state = initial_state
        best_state = initial_state
        
        # Cache das energias para evitar recálculos custosos em problemas complexos
        current_energy = current_state.energy
        best_energy = current_energy
        
        int_counter = 0
        idle_time = 0
        
        energy_history: list[float] = []
        energy_accepted_history: list[tuple[int, float]] = []

        logging.debug(f"[simulated annealing] Iniciando com temp inicial: {self._high_temp}, congelamento: {self._freezing_temp}, coeficiente: {self._freezing_coef}")
        logging.debug(f"[simulated annealing] Estado inicial: Energia={current_energy:.4f}")

        start_time = time.perf_counter()
        
        while temperature > self._freezing_temp and idle_time < self._max_idle_time:
            candidate_state = current_state.next_state()
            candidate_energy = candidate_state.energy

            if self._should_accept(current_energy, candidate_energy, temperature):
                current_state = candidate_state
                current_energy = candidate_energy

                if current_energy < best_energy:
                    best_state = current_state
                    best_energy = current_energy
                    idle_time = 0
                else:
                    if idle:
                        idle_time += 1
                
                
            else:
                if idle:
                    idle_time += 1
            
            energy_accepted_history.append(current_energy)
            energy_history.append(current_energy)
            temperature *= self._freezing_coef
            int_counter += 1

        # Cálculo do tempo movido para fora do loop
        execution_time = time.perf_counter() - start_time

        logging.debug(f"[simulated annealing] Melhor estado: Energia={best_energy:.4f}, em {int_counter} iterações")
        
        return Response(
            initial_state=initial_state,
            best_state=best_state,
            initial_energy=initial_state.energy,
            best_energy=best_energy,
            iterations=int_counter,
            high_temp=self._high_temp,
            temperature=temperature,
            freezing_temp=self._freezing_temp,
            freezing_coef=self._freezing_coef,
            energy_history=energy_history,
            energy_accepted_history=energy_accepted_history,
            execution_time=execution_time
        )

    def _should_accept(self, old_energy: float, new_energy: float, temperature: float) -> bool:
        if new_energy < old_energy:
            return True

        delta_e = new_energy - old_energy
        probability = math.exp(-delta_e / temperature)
        return random.random() <= probability