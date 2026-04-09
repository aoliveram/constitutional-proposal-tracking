import json
import networkx as nx
import matplotlib.pyplot as plt
import os

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/playground/research-proposal-implementation"
net_file = os.path.join(base_dir, "C1_dynamic_networks.json")

with open(net_file, 'r', encoding='utf-8') as f:
    waves = json.load(f)

# Extract node list across all waves
all_nodes = set()
for t_label, edges in waves.items():
    for edge in edges:
        all_nodes.add(edge['source'])
        all_nodes.add(edge['target'])

# Use the last wave for layout
last_wave = list(waves.keys())[-1]
G_last = nx.Graph()
G_last.add_nodes_from(all_nodes)
for edge in waves[last_wave]:
    G_last.add_edge(edge['source'], edge['target'], weight=edge['weight'])

pos = nx.spring_layout(G_last, seed=42)

frames = []
for t_label, edges in waves.items():
    G = nx.Graph()
    G.add_nodes_from(all_nodes)
    for edge in edges:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
    plt.figure(figsize=(10, 10))
    # Extract weights for edge widths
    edge_weights = [G[u][v].get('weight', 1) for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    linewidths = [2 * (w / max_weight) for w in edge_weights]
    
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color='lightblue')
    nx.draw_networkx_edges(G, pos, width=linewidths, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=6)
    
    plt.title(f"Network Evolution: {t_label}")
    plt.axis('off')
    
    frame_path = os.path.join(base_dir, f"frame_{t_label}.png")
    plt.savefig(frame_path, bbox_inches='tight')
    plt.close()
    frames.append(frame_path)

# Create GIF using PIL
from PIL import Image
images = [Image.open(f) for f in frames]
if images:
    gif_path = os.path.join(base_dir, "C1_network_evolution.gif")
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=1000, # 1 second per wave
        loop=0
    )
    print(f"GIF saved to {gif_path}")

# Clean up
for f in frames:
    if os.path.exists(f):
        os.remove(f)
