import pandas as pd
import logging
import matplotlib.pyplot as plt
from algorithm.smt_state import SMTState
from tools.state_metrics import StateMetrics  # Importe a nova classe

def table_kpi_comparison(estado_historico: SMTState, estado_otimizado: SMTState, save_path: str) -> None:
    metrics_hist = StateMetrics(estado_historico)
    metrics_opt = StateMetrics(estado_otimizado)
    
    data = {
        "Métrica (KPI)": [
            "Energia Total (Função Objetivo)",
            "Makespan Máximo (Tempo da Pior Linha)",
            "Desbalanceamento de Carga (σ)",
            "Tempo Gasto em Setup (Transições)",
            "Penalidade de Produtos Não Alocados"
        ],
        "Histórico (Humano)": [
            metrics_hist.total_energy,
            metrics_hist.max_makespan,
            metrics_hist.load_imbalance,
            metrics_hist.total_setup_cost,
            metrics_hist.unallocated_penalty
        ],
        "Otimizado (SA)": [
            metrics_opt.total_energy,
            metrics_opt.max_makespan,
            metrics_opt.load_imbalance,
            metrics_opt.total_setup_cost,
            metrics_opt.unallocated_penalty
        ]
    }

    df = pd.DataFrame(data)

    # Função interna para calcular o ganho percentual
    def calculate_improvement(hist, otim):
        if pd.isna(hist) or pd.isna(otim) or hist == 0:
            return "N/A"
        gain = ((hist - otim) / hist) * 100
        return f"{gain:.2f}%"

    # Aplica o cálculo de ganho para criar a 4ª coluna
    df["Ganho de Eficiência (%)"] = df.apply(
        lambda row: calculate_improvement(row["Histórico (Humano)"], row["Otimizado (SA)"]), 
        axis=1
    )

    # Arredonda as colunas numéricas
    df["Histórico (Humano)"] = df["Histórico (Humano)"].apply(lambda x: round(x, 2))
    df["Otimizado (SA)"] = df["Otimizado (SA)"].apply(lambda x: round(x, 2))

    # Salva em CSV
    csv_path = save_path.replace('.png', '.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    # Plota e Salva a Imagem (Mantém a lógica de imagem que te passei antes)
    # _save_dataframe_as_image(df, save_path)

def _save_dataframe_as_image(df: pd.DataFrame, save_path: str):
    """Função auxiliar para plotar o DataFrame do Pandas como uma imagem estática"""
    fig, ax = plt.subplots(figsize=(10, 3)) # Tamanho ideal para tabela
    ax.axis('tight')
    ax.axis('off')
    
    # Renderiza a tabela
    table = ax.table(
        cellText=df.values, 
        colLabels=df.columns, 
        cellLoc='center', 
        loc='center',
        colColours=['#f2f2f2']*len(df.columns)
    )
    
    # Estilização
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5) # Ajusta espaçamento das células
    
    # Deixa o cabeçalho em negrito
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')

    plt.title("Comparativo de KPIs: Baseline Humano vs. Simulated Annealing", pad=20, weight='bold')
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"Tabela de KPIs (PNG) salva em: {save_path}")
    finally:
        plt.close()