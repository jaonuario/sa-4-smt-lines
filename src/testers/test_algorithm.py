import logging
import random
from typing import Any

from core.base_tester import BaseTester
from core.simulated_annealing import Response

from algorithm.smt_state import SMTState

from visualization.energy_plot import plot_energy_convergence
from visualization.bar_chart import plot_workload_metrics, plot_granular_workload
from visualization.tables import table_responses
from visualization.state_repr import plot_state_route_graph, plot_side_by_side_comparison

from tools.loader import ScenarioBuilder


class AlgorithmTester(BaseTester):
    def __init__(self, num_runs: int = 30):
        super().__init__(test_name="algorithm_test")
        self.num_runs = num_runs
        self.seed = True
        self.seed_base = 10

    def generate_scenarios(self) -> list[tuple[dict[str, Any], SMTState, dict[str, Any]]]:
        builder_real = ScenarioBuilder(num_lines=3, full=False)
        builder_synth = ScenarioBuilder(num_lines=3, full=True)
        scenarios = []
        
        kwargs = {
            "high_temp": 1000.0,
            "freezing_temp": 0.01,
            "freezing_coef": 0.9995,
            "idle": True
        }
        
        for i in range(1, self.num_runs + 1):
            alloc, ops = builder_real.load_basic("production_plan.csv")
            state = SMTState(allocations=alloc, product_orders=ops)
            seed = self.run_seed(i)
            metadata = {"name": f"real_{i}", "is_synthetic": False, "seed": seed}
            scenarios.append((metadata, state, {**kwargs, "seed": seed}))

        for i in range(1, self.num_runs + 1):
            alloc, ops = builder_synth.load_basic("production_plan.csv")
            state = SMTState(allocations=alloc, product_orders=ops)
            seed = self.run_seed(i)
            metadata = {"name": f"synt_{i}", "is_synthetic": True, "seed": seed}
            scenarios.append((metadata, state, {**kwargs, "seed": seed}))
            
        logging.info(f"[{self.test_name}] Preparados {len(scenarios)} cenários de execução totalmente independentes.")
        return scenarios

    def process_results(self, results: list[tuple[dict[str, Any], Response]]) -> None:
        if not results:
            logging.error(f"[{self.test_name}] Sem resultados válidos para processar.")
            return
            
        real_results = [(meta, res) for meta, res in results if not meta["is_synthetic"]]
        synth_results = [(meta, res) for meta, res in results if meta["is_synthetic"]]
        
        if real_results:
            self.export_data(real_results, subdir="real")
        if synth_results:
            self.export_data(synth_results, subdir="synthetic")

    def export_data(self, results, subdir: str):
        best_meta, best_res = min(results, key=lambda x: x[1].best_energy)
        worst_meta, worst_res = max(results, key=lambda x: x[1].best_energy)
        
        comparative_data = [
            ("best", best_res), 
            ("worst", worst_res)
        ]

        logging.info(f"[{self.test_name} - {subdir}] Melhor: {best_meta['name']} ({best_res.best_energy:.2f})")
        logging.info(f"[{self.test_name} - {subdir}] Pior: {worst_meta['name']} ({worst_res.best_energy:.2f})")

        for key, result in comparative_data:
            plot_side_by_side_comparison(
                state=result.best_state, 
                save_path=self.get_save_path(subdir=subdir, filename=f'{key}_state_comparative_{subdir}.png')
            )

            plot_energy_convergence(
                energy_history=result.energy_accepted_history,
                save_path=self.get_save_path(subdir=subdir, filename=f'{key}_energy_convergence_{subdir}.png')
            )
            
            plot_workload_metrics(
                result.best_state, 
                save_path=self.get_save_path(subdir=subdir, filename=f'{key}_workload_metrics_{subdir}.png')
            )
            
            plot_granular_workload(
                result.best_state, 
                save_path=self.get_save_path(subdir=subdir, filename=f'{key}_granular_workload_metrics_{subdir}.png')
            )
            
        table_responses(results=results, save_path=self.get_save_path(subdir=subdir, filename='responses_table.csv'))
