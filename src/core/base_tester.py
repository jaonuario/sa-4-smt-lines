from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any
import logging

from core.simulated_annealing import State, Response 

class BaseTester(ABC):
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.root_dir = Path(__file__).resolve().parent.parent.parent
        self.test_dir: Path | None = None 
        self.seed = True
        self.seed_base = 1

    def run_seed(self, run_index: int) -> int | None:
        return self.seed_base + run_index if self.seed else None

    def _setup_directory(self) -> None:
        self.test_dir = self.root_dir / "test_results" / f"{self.test_name}"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def get_save_path(self, filename: str, subdir: str | None = None) -> str:
        if self.test_dir is None:
            self._setup_directory()
        
        target_dir = self.test_dir
        
        if subdir:
            target_dir = self.test_dir / subdir

            target_dir.mkdir(parents=True, exist_ok=True)
            
        return str(target_dir / filename)

    @abstractmethod
    def generate_scenarios(self) -> list[tuple[dict[str, Any], State, dict[str, Any]]]:
        pass

    @abstractmethod
    def process_results(self, results: list[tuple[dict[str, Any], Response]]) -> None:
        pass
