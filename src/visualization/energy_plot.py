import logging
import matplotlib.pyplot as plt

def plot_energy_convergence(energy_history: list[float], save_path: str, baseline_energy: float | None = None) -> None:
    if not energy_history:
        logging.warning("O histórico de energia está vazio. Gráfico não gerado.")
        return

    plt.figure(figsize=(10, 6))

    iteracoes = list(range(1, len(energy_history) + 1))

    plt.plot(
        iteracoes, 
        energy_history, 
        color='#1f77b4',
        marker='.',
        linestyle='-',
        linewidth=0.8,
        markersize=3,
        alpha=0.8,
        label="Energia Otimizada (SA)"
    )

    if baseline_energy is not None:
        plt.axhline(
            y=baseline_energy, 
            color='#d62728',
            linestyle='--',
            linewidth=1.5,
            alpha=0.9,
            label=f"Baseline Humano ({baseline_energy:.0f})"
        )
        plt.title("Convergência do Simulated Annealing vs Baseline Humano", fontsize=14, pad=15)
    else:
        plt.title("Evolução da Energia no Simulated Annealing", fontsize=14, pad=15)

    plt.xlabel("Iterações", fontsize=12)
    plt.ylabel("Energia Total (Custo de Setup + Penalidades)", fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper right", fontsize=10)
    
    plt.tight_layout()

    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"Gráfico de convergência de energia salvo em: {save_path}")
    except Exception as e:
        logging.error(f"Falha ao salvar gráfico de energia: {e}")
    finally:
        plt.close()
