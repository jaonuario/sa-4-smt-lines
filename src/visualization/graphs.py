import logging
import networkx as nx
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import colorsys
from typing import List, Tuple


def _get_oven_code_collors(oven_codes: list[str]) -> dict[str, str]:
    """
    Gera um mapeamento de cores para códigos de forno.
    Códigos com o mesmo prefixo recebem a mesma matiz (cor base),
    mas com variações de luminosidade (tons diferentes).
    """
    groups = {}
    unique_codes = list(dict.fromkeys(oven_codes))
    
    for code in unique_codes:
        prefix = code.split('_')[0]
        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(code)
        
    colors_map = {}
    num_prefixes = len(groups)
    
    for i, (prefix, codes) in enumerate(groups.items()):
        base_hue = i / num_prefixes if num_prefixes > 0 else 0.0
        num_codes = len(codes)
        
        for j, code in enumerate(codes):
            lightness = 0.6 if num_codes == 1 else 0.4 + (0.4 * (j / (num_codes - 1)))
            r, g, b = colorsys.hls_to_rgb(base_hue, lightness, 0.8)
            colors_map[code] = mcolors.to_hex((r, g, b))
            
    return colors_map


def plot_state_graph(state, save_path='solucao_completa.png'):
    """
    Gera um gráfico comparativo onde cada linha de produção tem duas visões:
    1. Visão por Forno (Cores Rehm)
    2. Visão por Prioridade (Gradiente de cores)
    """
    allocations = state.get_allocations()

    products = [op for line in allocations for op in line.products]
    oven_codes = [op.temperature_profile_code for op in products]

    linhas_ativas = [l for l in allocations if l.products or l.pinned_products]
    num_linhas = len(linhas_ativas)
    color_map = _get_oven_code_collors(oven_codes)


    if num_linhas == 0:
        print("Nenhuma linha com alocações para plotar.")
        return

    # Criamos 2 colunas de subplots (Esquerda: Forno | Direita: Prioridade). squeeze=False garante que axes seja matriz 2D
    fig, axes = plt.subplots(num_linhas, 2, figsize=(20, 5 * num_linhas), sharex=True, facecolor='none', squeeze=False)

    # 1. Preparação dos dados de prioridade para o gradiente
    all_prios = [op.priority for line in linhas_ativas for op in (line.pinned_products + line.products)]
    min_p, max_p = (min(all_prios), max(all_prios)) if all_prios else (1, 10)
    prio_cmap = plt.get_cmap('YlOrRd') # Amarelo (leve) -> Vermelho (urgente)
    prio_norm = mcolors.Normalize(vmin=min_p, vmax=max_p)

    for idx, line in enumerate(linhas_ativas):
        nome_linha = f"Linha {line.plan_line_id}"
        op_list = line.pinned_products + line.products
        
        # Criamos o grafo para esta linha específica
        G = nx.DiGraph()
        pos = {}
        labels = {}
        oven_colors = []
        priority_colors = []

        for x_idx, op in enumerate(op_list):
            node_id = f"{nome_linha}_{op.plan_item_id}"
            G.add_node(node_id)
            pos[node_id] = (x_idx, 0) # Tudo em uma linha horizontal
            labels[node_id] = f"{op.plan_item_id}\n(Prod:{op.product_id})"
            
            # Cor 1: Forno
            oven_code = op.temperature_profile_code
            oven_colors.append(color_map.get(oven_code, '#808080'))
            
            # Cor 2: Prioridade (Invertemos para Prio 1 ser Vermelho Escuro)
            p_color = prio_cmap(prio_norm(op.priority)) 
            priority_colors.append(p_color)

            if x_idx < len(op_list) - 1:
                G.add_edge(node_id, f"{nome_linha}_{op_list[x_idx+1].plan_item_id}")

        # --- Subplot da Esquerda: Visão de Forno ---
        ax_oven = axes[idx, 0]
        ax_oven.set_facecolor('none')
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=oven_colors, 
                               edgecolors='black', ax=ax_oven)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, ax=ax_oven)
        #nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, font_weight='bold', ax=ax_oven)
        ax_oven.set_title(f"{nome_linha.upper()} - Visão Forno", fontsize=12)
        ax_oven.axis('off')

        # --- Subplot da Direita: Visão de Prioridade ---
        ax_prio = axes[idx, 1]
        ax_prio.set_facecolor('none')
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=priority_colors, 
                               edgecolors='black', ax=ax_prio)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, ax=ax_prio)
        #nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, font_weight='bold', ax=ax_prio)
        ax_prio.set_title(f"{nome_linha.upper()} - Visão Prioridade", fontsize=12)
        ax_prio.axis('off')

    # Adiciona legenda de prioridade no canto inferior
    sm = plt.cm.ScalarMappable(cmap=prio_cmap, norm=prio_norm)
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02]) # [left, bottom, width, height]
    cbar_ax.set_facecolor('none')
    fig.colorbar(sm, cax=cbar_ax, orientation='horizontal', label='Nível de Prioridade (Mais Escuro = Menos Urgente)')

    #plt.suptitle("Comparativo de Sequenciamento: Otimização de Setup vs. Prioridade de Entrega", fontsize=16, y=0.98)
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    plt.savefig(save_path, dpi=300, transparent=True)    
    plt.close()
    logging.info(f"[plot_state_graph] Gráfico comparativo gerado em: {save_path}")


def plot_variance_boxplot(data, title="Boxplot", ylabel="Valores", save_path='boxplot.png'):
    """
    Plota um gráfico Boxplot para analisar a distribuição, variância e outliers dos dados.
    """
    plt.figure(figsize=(8, 6))
    
    plt.boxplot(data, patch_artist=True, boxprops=dict(facecolor='#3498db', color='#2980b9'), medianprops=dict(color='#e74c3c', linewidth=2))
    plt.title(title, fontsize=14)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks([1], ['Execuções'], fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    
    plt.savefig(save_path, dpi=300, transparent=True)
    plt.close()
    logging.info(f"[plot_variance_boxplot] Gráfico Boxplot gerado em: {save_path}")


def plot_scalability_curve(data: dict, title: str = "Scalability Curve", xlabel: str = "X-axis", ylabel: str = "Y-axis", save_path: str = 'scalability_curve.png'):
    """
    Plota um gráfico de linha (Line plot) para demonstrar a escalabilidade do algoritmo
    com base no crescimento do tempo de execução em instâncias maiores.
    
    Args:
        data (dict): Dicionário mapeando os rótulos do eixo X (multiplicadores) para os tempos (eixo Y).
        title (str): Título do gráfico.
        xlabel (str): Rótulo do eixo X.
        ylabel (str): Rótulo do eixo Y.
        save_path (str): Caminho onde o gráfico será salvo.
    """
    plt.figure(figsize=(10, 6))
    
    x_labels = list(data.keys())
    y_values = list(data.values())
    
    plt.plot(x_labels, y_values, marker='o', linestyle='-', color='#e74c3c', linewidth=2, markersize=8)
    
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, transparent=True)
    plt.close()
    logging.info(f"[plot_scalability_curve] Gráfico de escalabilidade gerado em: {save_path}")


import matplotlib.pyplot as plt
from typing import List, Tuple

def plotar_multiplas_retas(
    dados: List[List[Tuple[float, float]]], 
    dataset_names: List[str], 
    path: str = 'name.png',
    normalizar_y: bool = True,
    espacamento_x: float = 0.05,
    title:str = ""
):
    """
    Gera um gráfico de linhas com pontos igualmente espaçados e deslocamento lateral.
    Se normalizado, usa a escala MaxAbs (de -1 a 1), preservando os valores 
    negativos e a posição do zero de cada dataset.
    
    :param dados: Lista contendo listas de tuplas de floats (x, y).
    :param dataset_names: Lista contendo os nomes de cada dataset para a legenda.
    :param path: Caminho/nome do arquivo onde a imagem será salva.
    :param normalizar_y: Se True, padroniza os valores de Y entre -1 e 1.
    :param espacamento_x: Distância no eixo X para afastar os pontos de datasets diferentes.
    """
    plt.figure(figsize=(10, 6))
    
    posicoes_x_referencia = None
    rotulos_x_referencia = None
    qtd_datasets = len(dados)
    
    for i, dataset in enumerate(dados):
        if not dataset:
            continue
            
        x_valores, y_valores = zip(*dataset)
        
        # Cálculo do deslocamento (offset) no eixo X
        offset = (i - (qtd_datasets - 1) / 2) * espacamento_x
        posicoes_atuais = [pos + offset for pos in range(len(dataset))]
        
        if posicoes_x_referencia is None:
            posicoes_x_referencia = list(range(len(dataset)))
            rotulos_x_referencia = x_valores
            
        nome_da_reta = dataset_names[i] if i < len(dataset_names) else f'Dataset {i + 1}'
        
        # LÓGICA DE NORMALIZAÇÃO ALTERADA (Max Absoluto)
        if normalizar_y:
            # Encontra o maior valor em módulo (ignora se é positivo ou negativo)
            max_abs = max(abs(y) for y in y_valores)
            
            if max_abs > 0:
                # Divide tudo pelo maior valor absoluto.
                # Isso mantém os negativos como negativos e positivos como positivos.
                y_plot = [y / max_abs for y in y_valores]
            else:
                # Se todos os valores forem zero
                y_plot = [0.0 for _ in y_valores]
        else:
            y_plot = y_valores
        
        # Plota a reta
        plt.plot(posicoes_atuais, y_plot, marker='o', label=nome_da_reta)
    
    # Arruma o eixo X
    if posicoes_x_referencia is not None and rotulos_x_referencia is not None:
        plt.xticks(posicoes_x_referencia, rotulos_x_referencia)
    
    # Textos e detalhes do gráfico
    if normalizar_y:
        plt.title(title)
        plt.ylabel('Escala Relativa (-1 a 1)')
    else:
        plt.title(title)
        plt.ylabel('Valores Absolutos de Y')
        
    plt.xlabel('Eixo X')
    plt.legend()
    plt.grid(True, alpha=0.5)
    
    # Salva o gráfico
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico gerado e salvo com sucesso em: '{path}'")


def plotar_multiplas_retas_simples(
    dados: List[List[Tuple[float, float]]], 
    dataset_names: List[str], 
    path: str = 'name.png',
    espacamento_x: float = 0.05
):
    """
    Gera um gráfico de linhas a partir de uma lista de datasets, onde cada dataset
    é uma lista de tuplas (x, y). Os pontos são plotados igualmente espaçados com
    um pequeno deslocamento lateral para evitar sobreposição.
    
    :param dados: Lista contendo listas de tuplas de floats (x, y).
    :param dataset_names: Lista contendo os nomes de cada dataset para a legenda.
    :param path: Caminho/nome do arquivo onde a imagem será salva.
    :param espacamento_x: Distância no eixo X para afastar os pontos de datasets diferentes.
    """
    plt.figure(figsize=(10, 6))
    
    # Variáveis para guardar a referência do eixo X do primeiro dataset
    posicoes_x_referencia = None
    rotulos_x_referencia = None
    
    # Obtém a quantidade total de datasets para o cálculo do offset
    qtd_datasets = len(dados)
    
    for i, dataset in enumerate(dados):
        if not dataset:
            continue
            
        x_valores, y_valores = zip(*dataset)
        
        # Cálculo do deslocamento (offset) para este dataset no eixo X
        offset = (i - (qtd_datasets - 1) / 2) * espacamento_x
        
        # Cria posições igualmente espaçadas (0, 1, 2...) somadas ao offset
        posicoes_atuais = [pos + offset for pos in range(len(dataset))]
        
        # Salva as posições puras (0, 1, 2...) para usar como rótulo no eixo inferior
        if posicoes_x_referencia is None:
            posicoes_x_referencia = list(range(len(dataset)))
            rotulos_x_referencia = x_valores
            
        nome_da_reta = dataset_names[i] if i < len(dataset_names) else f'Dataset {i + 1}'
        
        # Plota usando as novas posições ajustadas
        plt.plot(posicoes_atuais, y_valores, marker='o', label=nome_da_reta)
    
    # Substitui os números puros pelos valores originais de X no gráfico
    if posicoes_x_referencia is not None and rotulos_x_referencia is not None:
        plt.xticks(posicoes_x_referencia, rotulos_x_referencia)
    
    # Adicionando detalhes ao gráfico
    plt.title('Gráfico de Múltiplas Retas (Pontos Lado a Lado)')
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')
    plt.legend()
    plt.grid(True)
    
    # Salva o gráfico
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico gerado e salvo com sucesso em: '{path}'")