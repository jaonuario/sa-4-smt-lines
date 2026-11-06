import logging
import networkx as nx
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import colorsys
from typing import List, Tuple


def _get_oven_code_collors(oven_codes: list[str]) -> dict[str, str]:
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
    allocations = state.get_allocations()

    products = [op for line in allocations for op in line.products]
    oven_codes = [op.temperature_profile_code for op in products]

    linhas_ativas = [l for l in allocations if l.products or l.pinned_products]
    num_linhas = len(linhas_ativas)
    color_map = _get_oven_code_collors(oven_codes)

    if num_linhas == 0:
        print("Nenhuma linha com alocações para plotar.")
        return

    fig, axes = plt.subplots(num_linhas, 2, figsize=(20, 5 * num_linhas), sharex=True, facecolor='none', squeeze=False)

    all_prios = [op.priority for line in linhas_ativas for op in (line.pinned_products + line.products)]
    min_p, max_p = (min(all_prios), max(all_prios)) if all_prios else (1, 10)
    prio_cmap = plt.get_cmap('YlOrRd')
    prio_norm = mcolors.Normalize(vmin=min_p, vmax=max_p)

    for idx, line in enumerate(linhas_ativas):
        nome_linha = f"Linha {line.plan_line_id}"
        op_list = line.pinned_products + line.products
        
        G = nx.DiGraph()
        pos = {}
        labels = {}
        oven_colors = []
        priority_colors = []

        for x_idx, op in enumerate(op_list):
            node_id = f"{nome_linha}_{op.plan_item_id}"
            G.add_node(node_id)
            pos[node_id] = (x_idx, 0)
            labels[node_id] = f"{op.plan_item_id}\n(Prod:{op.product_id})"
            
            oven_code = op.temperature_profile_code
            oven_colors.append(color_map.get(oven_code, '#808080'))
            
            p_color = prio_cmap(prio_norm(op.priority)) 
            priority_colors.append(p_color)

            if x_idx < len(op_list) - 1:
                G.add_edge(node_id, f"{nome_linha}_{op_list[x_idx+1].plan_item_id}")

        ax_oven = axes[idx, 0]
        ax_oven.set_facecolor('none')
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=oven_colors, 
                               edgecolors='black', ax=ax_oven)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, ax=ax_oven)
        ax_oven.set_title(f"{nome_linha.upper()} - Visão Forno", fontsize=12)
        ax_oven.axis('off')

        ax_prio = axes[idx, 1]
        ax_prio.set_facecolor('none')
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=priority_colors, 
                               edgecolors='black', ax=ax_prio)
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, ax=ax_prio)
        ax_prio.set_title(f"{nome_linha.upper()} - Visão Prioridade", fontsize=12)
        ax_prio.axis('off')

    sm = plt.cm.ScalarMappable(cmap=prio_cmap, norm=prio_norm)
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])
    cbar_ax.set_facecolor('none')
    fig.colorbar(sm, cax=cbar_ax, orientation='horizontal', label='Nível de Prioridade (Mais Escuro = Menos Urgente)')

    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    plt.savefig(save_path, dpi=300, transparent=True)    
    plt.close()
    logging.info(f"[plot_state_graph] Gráfico comparativo gerado em: {save_path}")


def plot_variance_boxplot(data, title="Boxplot", ylabel="Valores", save_path='boxplot.png'):
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
    plt.figure(figsize=(10, 6))
    
    posicoes_x_referencia = None
    rotulos_x_referencia = None
    qtd_datasets = len(dados)
    
    for i, dataset in enumerate(dados):
        if not dataset:
            continue
            
        x_valores, y_valores = zip(*dataset)
        
        offset = (i - (qtd_datasets - 1) / 2) * espacamento_x
        posicoes_atuais = [pos + offset for pos in range(len(dataset))]
        
        if posicoes_x_referencia is None:
            posicoes_x_referencia = list(range(len(dataset)))
            rotulos_x_referencia = x_valores
            
        nome_da_reta = dataset_names[i] if i < len(dataset_names) else f'Dataset {i + 1}'
        
        if normalizar_y:
            max_abs = max(abs(y) for y in y_valores)
            
            if max_abs > 0:
                y_plot = [y / max_abs for y in y_valores]
            else:
                y_plot = [0.0 for _ in y_valores]
        else:
            y_plot = y_valores
        
        plt.plot(posicoes_atuais, y_plot, marker='o', label=nome_da_reta)
    
    if posicoes_x_referencia is not None and rotulos_x_referencia is not None:
        plt.xticks(posicoes_x_referencia, rotulos_x_referencia)
    
    if normalizar_y:
        plt.title(title)
        plt.ylabel('Escala Relativa (-1 a 1)')
    else:
        plt.title(title)
        plt.ylabel('Valores Absolutos de Y')
        
    plt.xlabel('Eixo X')
    plt.legend()
    plt.grid(True, alpha=0.5)
    
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico gerado e salvo com sucesso em: '{path}'")


def plotar_multiplas_retas_simples(
    dados: List[List[Tuple[float, float]]], 
    dataset_names: List[str], 
    path: str = 'name.png',
    espacamento_x: float = 0.05
):
    plt.figure(figsize=(10, 6))
    
    posicoes_x_referencia = None
    rotulos_x_referencia = None
    
    qtd_datasets = len(dados)
    
    for i, dataset in enumerate(dados):
        if not dataset:
            continue
            
        x_valores, y_valores = zip(*dataset)
        
        offset = (i - (qtd_datasets - 1) / 2) * espacamento_x
        
        posicoes_atuais = [pos + offset for pos in range(len(dataset))]
        
        if posicoes_x_referencia is None:
            posicoes_x_referencia = list(range(len(dataset)))
            rotulos_x_referencia = x_valores
            
        nome_da_reta = dataset_names[i] if i < len(dataset_names) else f'Dataset {i + 1}'
        
        plt.plot(posicoes_atuais, y_valores, marker='o', label=nome_da_reta)
    
    if posicoes_x_referencia is not None and rotulos_x_referencia is not None:
        plt.xticks(posicoes_x_referencia, rotulos_x_referencia)
    
    plt.title('Gráfico de Múltiplas Retas (Pontos Lado a Lado)')
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')
    plt.legend()
    plt.grid(True)
    
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico gerado e salvo com sucesso em: '{path}'")
