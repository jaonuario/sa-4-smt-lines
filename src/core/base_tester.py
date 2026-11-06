from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
import logging

# 1. Importe as suas classes base abstratas/dataclasses
from core.simulated_annealing import State, Response 

class BaseTester(ABC):
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.test_dir: Path | None = None 
        self.seed = True
        self.seed_base = 1

    def run_seed(self, run_index: int) -> int | None:
        """
        Semente da execução `run_index`. Deve ser passada em kwargs["seed"] para
        ser aplicada DENTRO do processo worker (o random do processo principal não
        é herdado pelos workers no Windows). Cada rodada recebe uma semente
        distinta; a mesma rodada sempre recebe a mesma semente.
        """
        return self.seed_base + run_index if self.seed else None

    def _setup_directory(self) -> None:
        self.test_dir = self.root_dir / "test_results" / f"{self.test_name}"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def get_save_path(self, filename: str, subdir: str | None = None) -> str:
        """
        Retorna o caminho completo para o arquivo.
        Se 'subdir' for fornecido, cria um subdiretório dentro de self.test_dir.
        """
        if self.test_dir is None:
            self._setup_directory()
        
        target_dir = self.test_dir
        
        if subdir:
            target_dir = self.test_dir / subdir
            
            # Se o caminho existe e é um arquivo, precisamos removê-lo 
            # para poder criar o diretório no lugar
            # if target_dir.exists() and not target_dir.is_dir():
            #     target_dir.unlink() 
            
            # Agora criamos com segurança
            target_dir.mkdir(parents=True, exist_ok=True)
            
        return str(target_dir / filename)

    @abstractmethod
    def generate_scenarios(self) -> list[tuple[dict[str, Any], State, dict[str, Any]]]:
        """
        Contrato rigoroso:
        - dict[str, Any]: metadata (ex: {"linha": "SMD1", "produtos": 50})
        - State: O estado inicial do problema
        - dict[str, Any]: kwargs para o SimulatedAnnealing (ex: {"high_temp": 1000})
        """
        pass

    @abstractmethod
    def process_results(self, results: list[tuple[dict[str, Any], Response]]) -> None:
        """
        Recebe a lista validada pelo Runner.
        Cada tupla contém os metadados do cenário e o objeto Response oficial.
        """
        pass