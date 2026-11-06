import pandas as pd
import logging
import matplotlib.pyplot as plt
from algorithm.smt_state import SMTState
from tools.state_metrics import StateMetrics

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

    def calculate_improvement(hist, otim):
        if pd.isna(hist) or pd.isna(otim) or hist == 0:
            return "N/A"
        gain = ((hist - otim) / hist) * 100
        return f"{gain:.2f}%"

    df["Ganho de Eficiência (%)"] = df.apply(
        lambda row: calculate_improvement(row["Histórico (Humano)"], row["Otimizado (SA)"]), 
        axis=1
    )

    df["Histórico (Humano)"] = df["Histórico (Humano)"].apply(lambda x: round(x, 2))
    df["Otimizado (SA)"] = df["Otimizado (SA)"].apply(lambda x: round(x, 2))

    csv_path = save_path.replace('.png', '.csv')
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')


def _save_dataframe_as_image(df: pd.DataFrame, save_path: str):
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(
        cellText=df.values, 
        colLabels=df.columns, 
        cellLoc='center', 
        loc='center',
        colColours=['#f2f2f2']*len(df.columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')

    plt.title("Comparativo de KPIs: Baseline Humano vs. Simulated Annealing", pad=20, weight='bold')
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"Tabela de KPIs (PNG) salva em: {save_path}")
    finally:
        plt.close()
