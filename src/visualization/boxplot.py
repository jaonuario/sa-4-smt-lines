import matplotlib.pyplot as plt
import logging

def plot_variance_boxplot(dados_dict: dict, title: str, xlabel: str, ylabel: str, save_path: str):
    """
    Gera um Boxplot para avaliar a dispersão/variância dos resultados
    para diferentes categorias (ex: coeficientes de resfriamento).
    """
    # Extrai os rótulos (coeficientes) e as listas de valores (energias)
    labels = list(dados_dict.keys())
    data = list(dados_dict.values())
    
    plt.figure(figsize=(12, 7))
    
    # Cria o boxplot
    box = plt.boxplot(data, patch_artist=True, tick_labels=labels)
    
    # Customização visual para ficar com cara de artigo científico
    colors = ['#3498db'] * len(data) # Azul profissional
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        
    for median in box['medians']:
        median.set(color='#e74c3c', linewidth=2) # Mediana em vermelho
        
    for flier in box['fliers']:
        flier.set(marker='o', color='#e74c3c', alpha=0.5, markersize=5) # Outliers

    # Se a diferença entre o coef 0.6 e o 0.99 for gigantesca, 
    # descomente a linha abaixo para usar escala logarítmica no eixo Y:
    # plt.yscale('log')
        
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Rotaciona os labels do eixo X para não encavalar os números longos (ex: 0.9999995)
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # plt.tight_layout()
    plt.savefig(save_path, dpi=300, transparent=False)
    plt.close()
    
    logging.info(f"[plot_variance_boxplot] Gráfico salvo em: {save_path}")

import os
import matplotlib.pyplot as plt
from typing import Any

# def plot_variance_boxplot(
#     dados_dict: dict[str, Any], 
#     title: str, 
#     xlabel: str, 
#     ylabel: str, 
#     save_path: str
# ) -> None:
#     """
#     Gera um boxplot para avaliar a variância da energia (custo) encontrada 
#     nas múltiplas rodadas da Têmpera Simulada para cada semana.
#     """
#     labels = []
#     energy_data = []

#     # Ordenar as chaves para garantir que as semanas apareçam na ordem cronológica (wk16, wk17...)
#     for key in sorted(dados_dict.keys()):
#         # Limpar o nome do arquivo para usar como rótulo no eixo X (ex: 'wk16')
#         label = key.replace('.csv', '')
#         labels.append(label)

#         # Extrair apenas a energia (índice 1 da tupla) para a respectiva semana
#         energies = [item.best_energy for item in dados_dict[key]]
#         energy_data.append(energies)

#     # Configuração da figura
#     fig, ax = plt.subplots(figsize=(10, 6))
    
#     # Criar o boxplot
#     bplot = ax.boxplot(
#         energy_data, 
#         labels=labels, 
#         patch_artist=True,  # Permite preencher as caixas com cor
#         showmeans=True,     # Mostra o marcador da média
#         meanline=False
#     )

#     # Estilização para um aspecto mais industrial/acadêmico
#     colors = ['#4C72B0'] * len(labels)
#     for patch, color in zip(bplot['boxes'], colors):
#         patch.set_facecolor(color)
#         patch.set_alpha(0.7)

#     # Ajuste de bordas e marcadores
#     for median in bplot['medians']:
#         median.set(color='red', linewidth=2)
        
#     for mean in bplot['means']:
#         mean.set(marker='D', markeredgecolor='black', markerfacecolor='yellow')

#     # Configurações de texto e grid
#     ax.set_title(title, fontsize=14, fontweight='bold')
#     ax.set_xlabel(xlabel, fontsize=12)
#     ax.set_ylabel(ylabel, fontsize=12)
#     ax.grid(axis='y', linestyle='--', alpha=0.6)

#     # Garantir que o diretório de salvamento exista
#     os.makedirs(os.path.dirname(save_path), exist_ok=True)

#     # Salvar e fechar
#     plt.tight_layout()
#     plt.savefig(save_path, dpi=300)
#     plt.close()