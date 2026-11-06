import logging

from collections import defaultdict
from repository.historical_balancing_repository import HistoricalBalancingRepository
from core.base_tester import BaseTester
from core.simulated_annealing import Response
from tools.loader import ScenarioBuilder, HISTORICAL_FULL
from visualization.graphs import plotar_multiplas_retas, plotar_multiplas_retas_simples
from visualization.boxplot import plot_variance_boxplot

class FreezingCoefTester(BaseTester):
    def __init__(self):
        super().__init__(test_name="freezing_coef_tester")
        self.list_path = [
            'wk16.csv', 'wk17.csv', 'wk18.csv', 'wk19.csv', 'wk20.csv', 
            'wk22.csv', 'wk23.csv', 'wk24.csv', 'wk25.csv'
        ]
        self.loader = ScenarioBuilder(num_lines=3, full=HISTORICAL_FULL)

    def load_history(self):
        state_list = []
        for path in self.list_path:
            try:
                historical = HistoricalBalancingRepository().get_in_path(path)
                state, e_state = self.loader.load_historical(historical)
                state_list.append((path, e_state))
            except Exception as e:
                logging.exception(f"[{self.test_name}] Falha ao carregar histórico de {path}: {e}")
                continue
        return state_list

    def generate_scenarios(self, max_iterations=30) -> list:
        state_list = self.load_history()
        test_coef = [0.6, 0.85, 0.95, 0.98, 0.99, 0.995, 0.9995, 0.99995, 0.999995, 0.9999995]
        
        scenarios = []
        for name, state in state_list:
            for coef in test_coef:
                for iteracao in range(max_iterations):
                    seed = self.run_seed(iteracao)
                    metadata = {"filename": name, "iteracao": iteracao, "coef": coef, "seed": seed}
                    kwargs = {
                        "high_temp": 1000.0,
                        "freezing_temp": 0.01,
                        "freezing_coef": coef,
                        "seed": seed
                    }
                    
                    scenarios.append((metadata, state, kwargs))
                    
        return scenarios

    def process_results(self, resultados: list[tuple[dict, Response]]) -> None:
        results_dict = defaultdict(list)
        for metadata, resposta in resultados:
            filename = metadata["filename"]
            results_dict[filename].append(resposta)

        logging.info(f"[{self.test_name}] Gerando e salvando gráficos...")
        
        self.plot_best_energy(results_dict, self.get_save_path('best_energy.png'))
        self.plot_average_energy(results_dict, self.get_save_path('average_energy.png'))
        self.plot_gain_energy(results_dict, self.get_save_path('gain_energy.png'))
        self.plot_iterations_count(results_dict, self.get_save_path('count_iterations.png'))
        self.plot_exec_times(results_dict, self.get_save_path('execution_time.png'))


    def _build_dataset(self, results_dict, extract_func, aggregate_func):
        dataset = []
        for _, result_list in results_dict.items():
            grouped_data = defaultdict(list)
            for r in result_list:
                grouped_data[r.freezing_coef].append(extract_func(r))
            
            aggregated_list = []
            for coef, values in grouped_data.items():
                aggregated_list.append((coef, aggregate_func(values)))
            
            dataset.append(aggregated_list)
        return dataset

    def plot_best_energy(self, results, path):
        dataset = self._build_dataset(results, lambda r: r.best_energy, min)
        plotar_multiplas_retas(dados=dataset, dataset_names=list(results.keys()), path=path, title="Energia/Coef Congelamento(norm)")

    def plot_average_energy(self, results, path):
        dataset = self._build_dataset(results, lambda r: r.best_energy, lambda v: sum(v)/len(v))
        plotar_multiplas_retas(dados=dataset, dataset_names=list(results.keys()), path=path, title="Energia/Coef Congelamento(norm)")
    
    def plot_gain_energy(self, results, path):
        dataset = self._build_dataset(results, lambda r: r.initial_energy - r.best_energy, lambda v: sum(v)/len(v))
        plotar_multiplas_retas(dados=dataset, dataset_names=list(results.keys()), path=path, title="Ganho de energia/Coef Congelamente")

    def plot_iterations_count(self, results, path):
        dataset = self._build_dataset(results, lambda r: r.iterations, lambda v: sum(v)/len(v))
        plotar_multiplas_retas_simples(dados=dataset, dataset_names=list(results.keys()), path=path)
    
    def plot_exec_times(self, results, path):
        dataset = self._build_dataset(results, lambda r: r.execution_time, lambda v: sum(v)/len(v))
        plotar_multiplas_retas(dados=dataset, dataset_names=list(results.keys()), path=path, normalizar_y=False, title="Tempo de execução(norm)")
        
