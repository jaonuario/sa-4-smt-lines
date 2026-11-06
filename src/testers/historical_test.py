import logging
from typing import Any

from core.simulated_annealing import State, Response
from core.base_tester import BaseTester
from repository.historical_balancing_repository import HistoricalBalancingRepository
from tools.loader import ScenarioBuilder, HISTORICAL_FULL


class TestHistorico(BaseTester):
    def __init__(self):
        super().__init__(test_name="hist_vs_otimiz")
        self.num_runs = 30
        
        self.list_path = [
            'wk16.csv', 'wk17.csv', 'wk18.csv', 'wk19.csv', 'wk20.csv', 
            'wk22.csv', 'wk23.csv', 'wk24.csv', 'wk25.csv'
        ]
        self.repository = HistoricalBalancingRepository()

    def load_history(self):
        state_list = []
        for path in self.list_path:
            try:
                historical = self.repository.get_in_path(path)
                state, e_state = ScenarioBuilder(full=HISTORICAL_FULL).load_historical(historical)
                state_list.append((path, state, e_state))
            except Exception as e:
                logging.exception(f"[{self.test_name}] Falha ao carregar histórico de {path}: {e}")
                continue
        return state_list

    def generate_scenarios(self) -> list[tuple[dict[str, Any], State, dict[str, Any]]]:
        history = self.load_history()
        kwargs = {
                "high_temp": 10.0,
                "freezing_temp": 0.01,
                "freezing_coef": 0.9995,
                "idle": False
            }        
        scenarios = []
        for path, state, e_state in history:
            name = path.split('.')[0]
            for i in range(self.num_runs):
                seed = self.run_seed(i)
                metadata = {
                    "name": f"{name}_run_{i}",
                    "base_file": path,
                    "estado_historico": state,
                    "seed": seed
                }
                scenarios.append((metadata, e_state, {**kwargs, "seed": seed}))
            
        return scenarios

    def process_results(self, results: list[tuple[dict[str, Any], Response]]) -> None:
        if not results:
            logging.error(f"[{self.test_name}] Sem resultados válidos para processar.")
            return

        from collections import defaultdict
        
        weekly_energies = defaultdict(list)
        
        for metadata, response in results:
            semana = metadata["base_file"].replace('.csv', '') 
            weekly_energies[semana].append(response.best_energy)
            
        logging.info(f"[{self.test_name}] Resultados agrupados. Gerando Box Plot de variância...")

        try:
            from visualization.boxplot import plot_variance_boxplot
            
            sorted_weeks = sorted(weekly_energies.keys())
            dados_ordenados = {wk: weekly_energies[wk] for wk in sorted_weeks}
            
            save_path = self.get_save_path("variance_semanas.png")
            
            plot_variance_boxplot(
                dados_dict=dados_ordenados,
                title=f"Robustez Estocástica - Variância da Energia por Semana ({self.num_runs} Rodadas)",
                xlabel="Semanas Históricas",
                ylabel="Energia Final",
                save_path=save_path
            )
            logging.info(f"[{self.test_name}] Gráfico salvo em {save_path}")
            
        except ImportError:
            import matplotlib.pyplot as plt
            
            sorted_weeks = sorted(weekly_energies.keys())
            data_to_plot = [weekly_energies[wk] for wk in sorted_weeks]
            
            save_path = self.get_save_path("variance_semanas.png")
            
            plt.figure(figsize=(12, 6))
            plt.boxplot(data_to_plot, labels=sorted_weeks)
            
            plt.title("Robustez Estocástica - Variância da Energia por Semana (30 Rodadas)", fontsize=14)
            plt.xlabel("Semanas Históricas", fontsize=12)
            plt.ylabel("Energia Final", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            
            plt.savefig(save_path, dpi=300)
            plt.close()
            
            logging.info(f"[{self.test_name}] Gráfico de Boxplot salvo em {save_path}")
