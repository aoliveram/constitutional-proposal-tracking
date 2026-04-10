import json
import networkx as nx
import matplotlib.pyplot as plt
import os
from matplotlib.backends.backend_pdf import PdfPages
import math

base_dir = "/Users/anibaloliveramorales/Desktop/Doctorado/-Projects-/B - constitutional-proposal-tracking/playground/research-proposal-implementation"

def process_comision(c_name):
    net_file = os.path.join(base_dir, f"{c_name}_dynamic_networks_official.json")
    if not os.path.exists(net_file): return
    
    with open(net_file, 'r', encoding='utf-8') as f:
        waves = json.load(f)
        
    t_labels = list(waves.keys())
    last_t = t_labels[-1]
    
    # Use final network to find components and layout
    G_final = nx.Graph()
    for edge in waves[last_t]:
        G_final.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    # Get all nodes involved
    all_nodes = set()
    for label in waves:
        for edge in waves[label]:
            all_nodes.add(edge['source'])
            all_nodes.add(edge['target'])
    
    components = sorted(nx.connected_components(G_final), key=len, reverse=True)
    print(f"{c_name}: Found {len(components)} components.")
    
    # Fixed layout for the whole system (helps keep relative positions)
    pos_all = nx.spring_layout(G_final, seed=42, k=0.5)
    
    # Process top 3 components or all if less
    for i, component_nodes in enumerate(components[:3]):
        comp_id = i + 1
        pdf_path = os.path.join(base_dir, f"{c_name}_component_{comp_id}_evolution.pdf")
        
        # Subplot grid setup
        n_steps = len(t_labels)
        cols = 3
        rows = math.ceil(n_steps / cols)
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols*6, rows*6))
        fig.suptitle(f"{c_name} - Evolution of Component {comp_id}", fontsize=20)
        axes_flat = axes.flatten() if n_steps > 1 else [axes]
        
        for idx, t_label in enumerate(t_labels):
            ax = axes_flat[idx]
            
            # Subgraph for this component at this time step
            G_sub = nx.Graph()
            G_sub.add_nodes_from(component_nodes)
            for edge in waves[t_label]:
                if edge['source'] in component_nodes and edge['target'] in component_nodes:
                    G_sub.add_edge(edge['source'], edge['target'], weight=edge['weight'])
            
            # Sub-layout: clip global layout to component nodes
            pos_sub = {n: pos_all[n] for n in component_nodes if n in pos_all}
            
            weights = [G_sub[u][v].get('weight', 1) for u, v in G_sub.edges()]
            max_w = max(weights) if weights else 1
            l_widths = [3 * (w / max_w) for w in weights]
            
            nx.draw_networkx_nodes(G_sub, pos_sub, ax=ax, node_size=100, node_color='orange', alpha=0.8)
            nx.draw_networkx_edges(G_sub, pos_sub, ax=ax, width=l_widths, alpha=0.4, edge_color='black')
            nx.draw_networkx_labels(G_sub, pos_sub, ax=ax, font_size=8)
            
            ax.set_title(f"Step {idx}: {t_label}", fontsize=12)
            ax.axis('off')
            
        # Hide extra subplots
        for j in range(idx + 1, len(axes_flat)):
            axes_flat[j].axis('off')
            
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(pdf_path)
        plt.close()
        print(f"Saved PDF: {pdf_path}")

for c in ["C1", "C3"]:
    process_comision(c)
