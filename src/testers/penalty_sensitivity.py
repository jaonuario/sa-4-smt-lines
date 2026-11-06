import logging

from core.base_tester import BaseTester
# Presumo que o seu Runner chamará o SA, mas mantive as importações necessárias
from algorithm.smt_state import SMTState
from entities.penalty import Penalty

from visualization.dots_graph import plot_dots_graph
from visualization.bar_chart import plot_workload_metrics
from visualization.tables import table_responses
from visualization.state_repr import plot_state_route_graph, NodeColorAttribute

from tools.loader import basic_loader

class PenaltySensitivityTester(BaseTester):
    def __init__(self):
        super().__init__(test_name="penalty_sensitivity_test")

    def generate_scenarios(self) -> list[tuple[dict, any, dict]]:
        """
        Define os cenários extremos de penalidade para testar o 'relevo' da função objetivo.
        """
        logging.info(f"[{self.test_name}] Gerando cenários de estresse para as penalidades...")
        
        # 1. Definição dos Cenários (Análise de Sensibilidade baseada em proporções)
        scenarios_configs = {
            "1_Balanceado": Penalty(
                PRIORITY_PENALTY=1.0, CONVEYOR_PENALTY=1.0, PANEL_PENALTY=1.0, 
                PASTE_PENALTY=1.0, OVEN_PENALTY=1.0, TYPE_OVEN_PENALTY=1.0
            ),
            "2_Foco_Absoluto_Prioridade": Penalty(
                PRIORITY_PENALTY=100.0, CONVEYOR_PENALTY=1.0, PANEL_PENALTY=1.0, 
                PASTE_PENALTY=1.0, OVEN_PENALTY=1.0, TYPE_OVEN_PENALTY=1.0
            ),
            "3_Foco_Absoluto_Forno": Penalty(
                PRIORITY_PENALTY=1.0, CONVEYOR_PENALTY=1.0, PANEL_PENALTY=1.0, 
                PASTE_PENALTY=1.0, OVEN_PENALTY=100.0, TYPE_OVEN_PENALTY=100.0
            ),
            "4_Ignorar_Prioridade": Penalty(
                PRIORITY_PENALTY=0.0, CONVEYOR_PENALTY=1.0, PANEL_PENALTY=1.0, 
                PASTE_PENALTY=1.0, OVEN_PENALTY=1.0, TYPE_OVEN_PENALTY=1.0
            )
        }

        # 2. Parâmetros fixos do Simulated Annealing para isolar as variáveis
        sa_kwargs = {
            "high_temp": 10000.0,
            "freezing_temp": 0.001,
            "freezing_coef": 0.9995
        }

        scenarios = []

        # 3. Montagem da lista de tuplas
        for scenario_name, penalty_config in scenarios_configs.items():
            # Carregamos do zero a cada loop para evitar referência cruzada na memória
            alloc, ops = basic_loader()
            state = SMTState(allocations=alloc, product_orders=ops, penalty=penalty_config)
            
            # O metadata carrega a identificação que usaremos lá no process_results
            metadata = {"scenario_name": scenario_name}
            
            scenarios.append((metadata, state, sa_kwargs))

        return scenarios

    def process_results(self, results: list[tuple[dict, any]]) -> None:
        """
        Recebe os resultados processados e gera as provas visuais (gráficos e tabelas).
        """
        logging.info(f"[{self.test_name}] Processando resultados e gerando gráficos...")
        
        all_responses = []

        for metadata, result in results:
            scenario_name = metadata["scenario_name"]
            all_responses.append(result)
            
            # Prefixo para organizar os arquivos na pasta
            prefix = f"{scenario_name}_"
            
            logging.info(f"[{self.test_name}] Plotando gráficos para: {scenario_name}")

            # Grafos de comportamento da restrição (A Prova Visual para a banca)
            plot_state_route_graph(
                state=result.best_state,
                color_attribute=NodeColorAttribute.PAINEL,
                save_path=self.get_save_path(f"{prefix}painel_best.png")
            )
            plot_state_route_graph(
                state=result.best_state,
                color_attribute=NodeColorAttribute.PRIORITY,
                save_path=self.get_save_path(f"{prefix}priority_best.png")
            )
            plot_state_route_graph(
                state=result.best_state,
                color_attribute=NodeColorAttribute.TEMPERATURE_PROFILE,
                save_path=self.get_save_path(f"{prefix}oven_profile_best.png")
            )

            # Métricas de Desempenho e Convergência
            plot_dots_graph(
                result.energy_accepted_history, 
                title=f"Evolução da Energia - {scenario_name}", 
                xlabel="Iteração", 
                ylabel="Energia", 
                dots_label="Energia Aceita", 
                save_path=self.get_save_path(f"{prefix}energy_history.png")
            )
            plot_workload_metrics(
                result.best_state, 
                save_path=self.get_save_path(f"{prefix}workload_metrics.png")
            )

        # Exportação da tabela consolidada com todos os cenários lado a lado
        table_responses(
            responses=all_responses, 
            save_path=self.get_save_path('resultado_consolidado_penalidades.csv')
        )
        
        logging.info(f"[{self.test_name}] Todos os resultados foram salvos com sucesso no diretório.")