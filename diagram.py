import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

# Nodes
nodes = ['User Interface (UI)', 'Main Application', 'Configuration Manager',
         'Orchestrator',  # Renamed from 'Workflow/Executor'
         'Data Ingestion',  # Renamed from 'Ingest Component'
         'Chunk Processor',
         'Embedding Engine',  # Reflects Text Embedding
         'Vector Database',  # Renamed from 'Storage Manager'
         'Retrieval Engine',
         'Logging Module',
         'Evaluation Module',
         'Response Generator / Model Selector',  # Renamed from 'Response Generator'
         'Feedback Collector',
         'External APIs']  # New Node

G.add_nodes_from(nodes)

# Edges
edges = [('User Interface (UI)', 'Main Application'),
         ('Main Application', 'Configuration Manager'),
         ('Main Application', 'Orchestrator'),
         ('Configuration Manager', 'Orchestrator'),  # New Edge
         ('Orchestrator', 'Data Ingestion'),
         ('Orchestrator', 'Chunk Processor'),
         ('Orchestrator', 'Embedding Engine'),
         ('Orchestrator', 'Vector Database'),
         ('Orchestrator', 'Retrieval Engine'),
         ('Orchestrator', 'Logging Module'),
         ('Orchestrator', 'Evaluation Module'),
         ('Orchestrator', 'Response Generator / Model Selector'),
         ('Orchestrator', 'External APIs'),  # New Edge
         ('Response Generator / Model Selector', 'User Interface (UI)'),
         ('User Interface (UI)', 'Feedback Collector'),
         ('Feedback Collector', 'Response Generator / Model Selector')]

G.add_edges_from(edges)

layouts = [nx.spring_layout, nx.circular_layout, nx.random_layout, nx.shell_layout, nx.kamada_kawai_layout, nx.spectral_layout]

for layout in layouts:
    plt.figure(figsize=(12, 12))
    pos = layout(G) if layout != nx.spring_layout else layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color=['red' if node == 'Orchestrator' else 'lightblue' for node in G.nodes],
            font_weight='bold', node_size=2000, font_size=10, font_color='black', edge_color='gray', arrows=True)
    plt.savefig(f'system_architecture_{layout.__name__.split("_")[0]}.png')

plt.show()
