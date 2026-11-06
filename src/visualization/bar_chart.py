import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def plot_workload_metrics(state, save_path='metricas_carga_trabalho.png'):
    """
    Gera um gráfico com 3 barras por linha: Setup, Produção (Empilhada por OP) e Total.
    """
    allocations = state.get_allocations()
    linhas = [f"Linha {line.plan_line_id}" for line in allocations]
    
    # Configurações de cores para as OPs (Usamos tab20 para ter 20 cores distintas)
    cmap = cm.get_cmap('tab20')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    x = np.arange(len(linhas))
    width = 0.25 

    tempo_setup_list = []
    tempo_total_list = []

    for idx, line in enumerate(allocations):
        op_list = line.pinned_products + line.products
        
        # 1. Cálculo do Setup
        s_time = 0.0
        for i in range(len(op_list) - 1):
            curr, next_op = op_list[i], op_list[i+1]
            s_time += (5.0 if curr.solder_paste_id != next_op.solder_paste_id else 0.0) + \
                      (5.0 if curr.painel_id != next_op.painel_id else 0.0) + \
                      curr.oven_transition_costs.get(next_op.temperature_profile_code, 0.0)
        tempo_setup_list.append(s_time)
        
        # 2. Empilhamento da Produção (Agregação por OP)
        bottom_val = 0.0
        p_time_total = 0.0
        
        for op in op_list:
            p_time = op.total_time.get(line.plan_line_id, 0.0)
            # Cor baseada no ID do produto para consistência visual
            color = cmap(op.product_id % 20)
            
            ax.bar(x[idx], p_time, width, bottom=bottom_val, 
                   color=color, edgecolor='white', linewidth=0.5)
            
            bottom_val += p_time
            p_time_total += p_time
            
        tempo_total_list.append(s_time + p_time_total)

    # 3. Desenhar barras de Setup e Total nas laterais
    ax.bar(x - width, tempo_setup_list, width, label='Setup', color='#e74c3c', hatch='//')
    ax.bar(x + width, tempo_total_list, width, label='Total', color='#2ecc71', alpha=0.6)

    # Estilização
    ax.set_ylabel('Tempo (minutos)', fontsize=12, fontweight='bold')
    ax.set_title('Distribuição de Carga: Setup, Produção por OP e Total', fontsize=14, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([l.upper() for l in linhas], fontsize=11)
    
    # Criar legenda personalizada (Setup, Total e uma amostra de OP)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e74c3c', hatch='//', label='Setup'),
        Patch(facecolor='#2ecc71', alpha=0.6, label='Tempo Total'),
        Patch(facecolor=cmap(0), label='Tempo de Produção (por OP)')
    ]
    ax.legend(handles=legend_elements, fontsize=10)
    
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    
    logging.info(f"[plot_workload_metrics] Gráfico empilhado gerado em: {save_path}")


import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def plot_granular_workload(state, save_path='carga_granular.png'):
    """
    Gera um gráfico de barras empilhadas:
    - Produção (cor única sólida)
    - Setup (cor distinta com hachura)
    """
    allocations = state.get_allocations()
    linhas = [f"Linha {line.plan_line_id}" for line in allocations]
    
    # Cores escolhidas para contraste profissional
    prod_color = '#3498db'  # Azul sólido único para produção
    setup_color = '#e74c3c' # Vermelho para setup
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for idx, line in enumerate(allocations):
        op_list = line.pinned_products + line.products
        bottom_val = 0.0
        
        for i, op in enumerate(op_list):
            # 1. Segmento de Produção (Cor Única)
            p_time = op.total_time.get(line.plan_line_id, 0.0)
            ax.bar(idx, p_time, 0.5, bottom=bottom_val, 
                   color=prod_color, edgecolor='white', linewidth=0.5)
            
            # Label opcional dentro da barra
            if p_time > 50:
                ax.text(idx, bottom_val + p_time/2, str(op.plan_item_id), 
                        ha='center', va='center', color='white', fontsize=8, fontweight='bold')
            
            bottom_val += p_time
            
            # 2. Segmento de Setup (Cores de Setup com Hachura)
            if i < len(op_list) - 1:
                next_op = op_list[i+1]
                s_time = (5.0 if op.solder_paste_id != next_op.solder_paste_id else 0.0) + \
                         (5.0 if op.painel_id != next_op.painel_id else 0.0) + \
                         op.oven_transition_costs.get(next_op.temperature_profile_code, 0.0)
                
                ax.bar(idx, s_time, 0.5, bottom=bottom_val, 
                       color=setup_color, edgecolor='white', hatch='//')
                bottom_val += s_time

    ax.set_ylabel('Tempo Total (Minutos)', fontsize=12)
    ax.set_title('Distribuição de Tempo: Produção (Agregada) vs Setup', fontsize=14, pad=20)
    ax.set_xticks(range(len(linhas)))
    ax.set_xticklabels(linhas, fontsize=11)
    
    # Legenda fixa
    legend_elements = [
        Patch(facecolor=prod_color, label='Produção'),
        Patch(facecolor=setup_color, hatch='//', label='Setup (Transição)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logging.info(f"[plot_granular_workload] Gráfico gerado em: {save_path}")