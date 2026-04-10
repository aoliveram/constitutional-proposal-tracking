import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from PIL import Image

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/playground/research-proposal-implementation/network-visualization"

def make_gif(c_name):
    net_file = os.path.join(base_dir, f"{c_name}_dynamic_networks.json")
    if not os.path.exists(net_file): return
    
    with open(net_file, 'r', encoding='utf-8') as f:
        waves = json.load(f)
    
    t_labels = list(waves.keys())
    
    # Global layout based on final state
    G_final = nx.Graph()
    for edge in waves[t_labels[-1]]:
        G_final.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    all_nodes = list(G_final.nodes())
    pos = nx.spring_layout(G_final, seed=42, k=0.5)
    
    frames = []
    for t_label in t_labels:
        G = nx.Graph()
        G.add_nodes_from(all_nodes)
        for edge in waves[t_label]:
            G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
            
        plt.figure(figsize=(12, 12))
        weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
        max_w = max(weights) if weights else 1
        l_widths = [4 * (w / max_w) for w in weights]
        
        nx.draw_networkx_nodes(G, pos, node_size=80, node_color='skyblue', edgecolors='white', linewidths=0.5)
        nx.draw_networkx_edges(G, pos, width=l_widths, alpha=0.3, edge_color='gray')
        nx.draw_networkx_labels(G, pos, font_size=5)
        
        plt.title(f"{c_name} Evolution: {t_label}", fontsize=20)
        plt.axis('off')
        
        temp_frame = os.path.join(base_dir, f"tmp_{c_name}_{t_label}.png")
        plt.savefig(temp_frame, bbox_inches='tight')
        plt.close()
        frames.append(temp_frame)
        
    # Convert to GIF
    images = [Image.open(f) for f in frames]
    gif_path = os.path.join(base_dir, f"{c_name}_network_evolution.gif")
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=1500, # slower for clarity
        loop=0
    )
    print(f"Saved GIF: {gif_path}")
    
    # Clean up
    for f in frames:
        if os.path.exists(f): os.remove(f)

for c in ["C1", "C3"]:
    make_gif(c)
