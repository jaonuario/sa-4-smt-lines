import logging
from matplotlib import pyplot as plt

def plot_dots_graph(data, title="Dots Graph", xlabel="X-axis", ylabel="Y-axis", dots_label="Dots", save_path='dots_graph.png', lower_bound=None):
    """
    Plota um gráfico de pontos (scatter plot) a partir dos dados fornecidos.
    
    Args:
        data (list of tuples): Lista de tuplas onde cada tupla contém (x, y) para um ponto.
        title (str): Título do gráfico.
        xlabel (str): Rótulo do eixo X.
        ylabel (str): Rótulo do eixo Y.
        lower_bound (float, optional): Valor para plotar a linha do Limite Inferior Teórico.
    """
    # Separar os dados em listas de x e y
    x, y = zip(*data)
    
    # Criar o gráfico de pontos
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=10, color='#e67e22', alpha=0.5, label=dots_label)
    
    # Configurações do gráfico
    plt.yscale('log')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    
    if lower_bound is not None:
        plt.axhline(y=lower_bound, color='red', linestyle='--', linewidth=2, label="Limite Inferior Teórico")
    plt.legend()

    # Exibir o gráfico
    plt.savefig(save_path, dpi=300, transparent=True)
    plt.close()

    logging.info(f"[plot_dots_graph] Gráfico de pontos gerado em: {save_path}")


def plot_multiple_dots_graph(datasets: dict, title="Multiple Dots Graph", xlabel="X-axis", ylabel="Y-axis", save_path='multiple_dots_graph.png', lower_bound=None):
    """
    Plota um gráfico de pontos (scatter plot) com múltiplos conjuntos de dados.
    
    Args:
        datasets (dict): Dicionário onde a chave é o rótulo da legenda e o valor é a lista de tuplas (x, y) para os pontos.
        title (str): Título do gráfico.
        xlabel (str): Rótulo do eixo X.
        ylabel (str): Rótulo do eixo Y.
        save_path (str): Caminho para salvar a imagem.
        lower_bound (float, optional): Valor para plotar a linha do Limite Inferior Teórico.
    """
    plt.figure(figsize=(12, 7))
    
    for label, data in datasets.items():
        if not data:
            continue
        x, y = zip(*data)
        # O matplotlib escolherá cores diferentes automaticamente para cada scatter plot
        plt.scatter(x, y, s=5, alpha=0.5, label=label)
        
    if lower_bound is not None:
        plt.axhline(y=lower_bound, color='red', linestyle='--', linewidth=2, label="Limite Inferior Teórico")

    plt.yscale('log')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left') # Coloca a legenda fora do gráfico para não cobrir os dados
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

    logging.info(f"[plot_multiple_dots_graph] Gráfico de pontos múltiplos gerado em: {save_path}")

