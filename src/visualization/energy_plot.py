import logging
import matplotlib.pyplot as plt

def plot_energy_convergence(energy_history: list[float], save_path: str, baseline_energy: float | None = None) -> None:
    """
    Gera e salva o gráfico específico de convergência de energia (custo) 
    do processo de Simulated Annealing.
    """
    if not energy_history:
        logging.warning("O histórico de energia está vazio. Gráfico não gerado.")
        return

    # Define o tamanho ideal para gráficos de relatório/TCC
    plt.figure(figsize=(10, 6))

    # O eixo X será o número da iteração
    iteracoes = list(range(1, len(energy_history) + 1))

    # Estilização focada em otimização (Linha fina + Pontos translúcidos)
    plt.plot(
        iteracoes, 
        energy_history, 
        color='#1f77b4',       # Azul clássico agradável para dados
        marker='.',            # Marcadores em ponto
        linestyle='-',         # Linha conectando os pontos
        linewidth=0.8,         # Linha fina para não poluir
        markersize=3,          # Pontos pequenos
        alpha=0.8,             # Leve transparência para destacar a densidade
        label="Energia Otimizada (SA)"
    )

    # NOVO: Adição da Linha de Base (Trabalho Humano)
    if baseline_energy is not None:
        plt.axhline(
            y=baseline_energy, 
            color='#d62728',         # Vermelho para destacar a diferença
            linestyle='--',          # Tracejado para diferenciar da curva do algoritmo
            linewidth=1.5,
            alpha=0.9,
            label=f"Baseline Humano ({baseline_energy:.0f})"
        )
        # Atualiza o título para refletir a comparação
        plt.title("Convergência do Simulated Annealing vs Baseline Humano", fontsize=14, pad=15)
    else:
        plt.title("Evolução da Energia no Simulated Annealing", fontsize=14, pad=15)

    # Textos de contexto de domínio chumbados
    plt.xlabel("Iterações", fontsize=12)
    plt.ylabel("Energia Total (Custo de Setup + Penalidades)", fontsize=12)
    
    # Adiciona grid para facilitar a leitura dos platôs de otimização
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc="upper right", fontsize=10)
    
    plt.tight_layout()

    # Salvamento seguro
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logging.info(f"Gráfico de convergência de energia salvo em: {save_path}")
    except Exception as e:
        logging.error(f"Falha ao salvar gráfico de energia: {e}")
    finally:
        # Libera a memória da RAM (CRÍTICO em loops do Runner)
        plt.close()