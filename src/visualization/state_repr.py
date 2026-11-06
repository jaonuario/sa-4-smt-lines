import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import colorsys
from enum import Enum

class NodeColorAttribute(Enum):
    TEMPERATURE_PROFILE = 'temperature_profile_code'
    SOLDER_PASTE = 'solder_paste_id'
    PAINEL = 'painel_id'
    PRIORITY = 'priority'
    PRODUCT = 'product_id'
    WIDTH = 'width'


def _get_shades_for_base_color(base_color, num_shades):
    rgb = mcolors.to_rgb(base_color)
    h, l, s = colorsys.rgb_to_hls(*rgb)
    
    shades = []
    if num_shades == 1:
        shades.append(mcolors.to_rgba(colorsys.hls_to_rgb(h, l, s)))
    else:
        l_min, l_max = 0.3, 0.8
        step = (l_max - l_min) / (num_shades - 1)
        for i in range(num_shades):
            new_l = l_min + i * step
            shades.append(mcolors.to_rgba(colorsys.hls_to_rgb(h, new_l, s)))
    return shades


def plot_temperature_route_graph(state, save_path):
    allocations = state.get_allocations()
    attr_name = NodeColorAttribute.TEMPERATURE_PROFILE.value
    
    unique_codes = set()
    for alloc in allocations:
        ops = alloc.pinned_products + alloc.products
        for op in ops:
            val = getattr(op, attr_name, None)
            if val is not None:
                unique_codes.add(val)
                
    unique_codes = sorted(list(unique_codes))
    
    base_to_codes = {}
    for code in unique_codes:
        base = str(code).split('_')[0]
        if base not in base_to_codes:
            base_to_codes[base] = []
        base_to_codes[base].append(code)
        
    cmap = plt.get_cmap('tab10')
    base_colors = {base: cmap(i / max(1, len(base_to_codes) - 1)) if len(base_to_codes) > 1 else cmap(0) 
                   for i, base in enumerate(base_to_codes.keys())}
    
    color_mapping = {}
    for base, codes in base_to_codes.items():
        shades = _get_shades_for_base_color(base_colors[base], len(codes))
        for code, shade in zip(codes, shades):
            color_mapping[code] = shade

    _draw_graph(state, attr_name, color_mapping, unique_codes, "Forno (Famílias por Cor / Versões por Tom)", save_path)


def plot_priority_route_graph(state, save_path):
    allocations = state.get_allocations()
    attr_name = NodeColorAttribute.PRIORITY.value

    unique_values = set()
    for alloc in allocations:
        ops = alloc.pinned_products + alloc.products
        for op in ops:
            val = getattr(op, attr_name, None)
            if val is not None:
                unique_values.add(val)

    try:
        unique_values = sorted(list(unique_values), key=float)
    except ValueError:
        unique_values = sorted(list(unique_values))

    cmap = plt.get_cmap('coolwarm')
    color_mapping = {}
    
    for i, val in enumerate(unique_values):
        norm = i / max(1, len(unique_values) - 1)        
        color_mapping[val] = cmap(1.0 - norm)

    _draw_graph(state, attr_name, color_mapping, unique_values, "Prioridade (Escala de Calor)", save_path)


def plot_standard_route_graph(state, color_attribute: NodeColorAttribute, save_path):
    allocations = state.get_allocations()
    attr_name = color_attribute.value

    unique_values = set()
    for alloc in allocations:
        ops = alloc.pinned_products + alloc.products
        for op in ops:
            val = getattr(op, attr_name, None)
            unique_values.add(val)

    unique_values = sorted(list(unique_values))
    cmap = plt.get_cmap('nipy_spectral')
    color_mapping = {
        val: cmap(i / max(1, len(unique_values) - 1)) if len(unique_values) > 1 else cmap(0) 
        for i, val in enumerate(unique_values)
    }
    
    _draw_graph(state, attr_name, color_mapping, unique_values, f"Atributo: {color_attribute.name}", save_path)


def _draw_graph(state, attr_name, color_mapping, unique_values, title_suffix, save_path):
    allocations = state.get_allocations()
    fig, ax = plt.subplots(figsize=(14, max(4, 1.5 * len(allocations)))) 
    G = nx.DiGraph()
    pos = {}
    node_colors = []
    labels = {}

    node_counter = 0

    for y_idx, alloc in enumerate(allocations):
        ops = alloc.pinned_products + alloc.products
        
        ax.plot([-0.5, max(0, len(ops) - 0.5)], [-y_idx, -y_idx], 
                color='#e0e0e0', linestyle=':', zorder=0)
        ax.text(-0.8, -y_idx, f"Linha {alloc.plan_line_id}", 
                fontsize=11, fontweight='bold', va='center', ha='right')

        for x_idx, op in enumerate(ops):
            node_id = node_counter 
            node_counter += 1
            
            G.add_node(node_id)
            pos[node_id] = (x_idx, -y_idx) 

            val = getattr(op, attr_name, None)
            node_colors.append(color_mapping.get(val, '#808080'))
            labels[node_id] = str(op.plan_item_id)

            if x_idx > 0:
                G.add_edge(node_id - 1, node_id)

    if G.nodes:
        nx.draw(G, pos, ax=ax, with_labels=True, labels=labels,
                node_color=node_colors, node_size=800, font_size=9,
                font_color='white', font_weight='bold', edge_color='#666666',
                arrows=True, arrowsize=15)

    if unique_values:
        legend_patches = [mpatches.Patch(color=color_mapping[val], label=str(val))
                         for val in unique_values if val in color_mapping]
        plt.legend(handles=legend_patches, loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)

    ax.set_title(f"Sequenciamento SMT - {title_suffix}", fontsize=14, pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_state_route_graph(state, color_attribute: NodeColorAttribute = NodeColorAttribute.TEMPERATURE_PROFILE, save_path='estado_grafo.png'):
    if color_attribute == NodeColorAttribute.TEMPERATURE_PROFILE:
        plot_temperature_route_graph(state, save_path)
    elif color_attribute == NodeColorAttribute.PRIORITY:
        plot_priority_route_graph(state, save_path)
    else:
        plot_standard_route_graph(state, color_attribute, save_path)

def plot_side_by_side_comparison(state, save_path, title = "Comparativo"):
    allocations = state.get_allocations()
    n_lines = len(allocations)
    
    fig, axes = plt.subplots(nrows=n_lines * 2, ncols=1, 
                             figsize=(14, 4 * n_lines), 
                             sharex=True, 
                             gridspec_kw={'hspace': 0.3})
    
    if n_lines == 1: axes = [axes]
    
    oven_cmap = plt.get_cmap('tab20')
    priority_cmap = plt.get_cmap('coolwarm')
    
    for i, alloc in enumerate(allocations):
        ops = alloc.pinned_products + alloc.products
        
        ax_oven = axes[i * 2]
        ax_prio = axes[i * 2 + 1]
        
        x = range(len(ops))
        oven_vals = sorted([op.temperature_profile_code for op in ops])
        prio_vals = [float(op.priority) for op in ops]
        
        ax_oven.step(x, oven_vals, where='post', color='teal', marker='o')
        ax_oven.set_title(f"Linha {alloc.plan_line_id} - Perfil de Forno", fontsize=10, fontweight='bold')
        ax_oven.grid(True, linestyle=':', alpha=0.6)
        
        ax_prio.bar(x, prio_vals, color='salmon', alpha=0.7)
        ax_prio.set_title(f"Linha {alloc.plan_line_id} - Prioridade (Quanto maior, mais urgente)", fontsize=10)
        ax_prio.grid(True, linestyle=':', alpha=0.6)
        
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
