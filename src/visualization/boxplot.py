import matplotlib.pyplot as plt
import logging

def plot_variance_boxplot(dados_dict: dict, title: str, xlabel: str, ylabel: str, save_path: str):
    labels = list(dados_dict.keys())
    data = list(dados_dict.values())
    
    plt.figure(figsize=(12, 7))
    
    box = plt.boxplot(data, patch_artist=True, tick_labels=labels)
    
    colors = ['#3498db'] * len(data)
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        
    for median in box['medians']:
        median.set(color='#e74c3c', linewidth=2)
        
    for flier in box['fliers']:
        flier.set(marker='o', color='#e74c3c', alpha=0.5, markersize=5)

    plt.title(title, fontsize=14, pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    plt.xticks(rotation=45)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(save_path, dpi=300, transparent=False)
    plt.close()
    
    logging.info(f"[plot_variance_boxplot] Gráfico salvo em: {save_path}")

import os
import matplotlib.pyplot as plt
from typing import Any
