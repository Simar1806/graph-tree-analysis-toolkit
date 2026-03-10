"""
Graph and Tree Analysis Toolkit
Flask Backend - Main Application
"""

from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64
import json
import heapq
from collections import defaultdict

app = Flask(__name__)

# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                facecolor='#0f1117', edgecolor='none', dpi=120)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64


def parse_graph_input(vertices_str, edges_str, directed=False, weighted=False):
    """Parse user input and return a NetworkX graph."""
    vertices = vertices_str.strip().split()
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    G.add_nodes_from(vertices)

    edges = []
    for line in edges_str.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.replace('-', ' ').split()
        if weighted:
            if len(parts) < 3:
                raise ValueError(f"Weighted edge must be 'U-V weight', got: '{line}'")
            u, v, w = parts[0], parts[1], float(parts[2])
            G.add_edge(u, v, weight=w)
        else:
            if len(parts) < 2:
                raise ValueError(f"Edge must be 'U-V', got: '{line}'")
            u, v = parts[0], parts[1]
            G.add_edge(u, v)
    return G


def draw_graph(G, title="Graph", highlight_nodes=None, highlight_edges=None,
               color_map=None, node_size=800):
    """Draw a NetworkX graph and return base64 image."""
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#0f1117')

    pos = nx.spring_layout(G, seed=42, k=2)

    # Node colors
    if color_map:
        palette = ['#ef4444','#3b82f6','#22c55e','#f59e0b','#a855f7',
                   '#06b6d4','#ec4899','#84cc16','#f97316','#14b8a6']
        color_list = list(set(color_map.values()))
        node_colors = [palette[color_list.index(color_map.get(n, 0)) % len(palette)]
                       for n in G.nodes()]
    elif highlight_nodes:
        node_colors = ['#22c55e' if n in highlight_nodes else '#3b82f6'
                       for n in G.nodes()]
    else:
        node_colors = '#3b82f6'

    # Edge colors
    if highlight_edges:
        edge_colors = ['#f59e0b' if (u, v) in highlight_edges or
                       (v, u) in highlight_edges else '#64748b'
                       for u, v in G.edges()]
    else:
        edge_colors = '#64748b'

    is_directed = isinstance(G, nx.DiGraph)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=node_size, ax=ax, alpha=0.95)
    nx.draw_networkx_labels(G, pos, font_color='white',
                            font_size=11, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                           width=2, ax=ax, arrows=True,
                           arrowsize=20, connectionstyle='arc3,rad=0.08' if is_directed else 'arc3,rad=0')

    # Draw edge weight labels
    if nx.is_weighted(G):
        labels = nx.get_edge_attributes(G, 'weight')
        labels = {k: f"{int(v) if v == int(v) else v}" for k, v in labels.items()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels,
                                     font_color='#f59e0b', font_size=9, ax=ax)

    ax.set_title(title, color='white', fontsize=14, fontweight='bold', pad=12)
    ax.axis('off')
    return fig_to_base64(fig)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/tools')
def tools():
    return render_template('tools.html')


@app.route('/tree')
def tree():
    return render_template('tree.html')


# ─────────────────────────────────────────────
# API: Graph Properties
# ─────────────────────────────────────────────

@app.route('/api/graph/properties', methods=['POST'])
def graph_properties():
    try:
        data = request.json
        G = parse_graph_input(
            data['vertices'], data['edges'],
            data.get('directed', False), data.get('weighted', False)
        )
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        degrees = {n: G.degree(n) for n in G.nodes()}
        if isinstance(G, nx.DiGraph):
            in_deg = {n: G.in_degree(n) for n in G.nodes()}
            out_deg = {n: G.out_degree(n) for n in G.nodes()}
        else:
            in_deg = out_deg = None

        connected = nx.is_connected(undirected)
        components = nx.number_connected_components(undirected)

        # Cycle detection
        try:
            cycle = nx.find_cycle(G)
            has_cycle = True
        except nx.NetworkXNoCycle:
            has_cycle = False

        img = draw_graph(G, "Graph Visualization")

        return jsonify({
            'success': True,
            'vertices': list(G.nodes()),
            'edges': list(G.edges()),
            'num_vertices': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'degrees': degrees,
            'in_degrees': in_deg,
            'out_degrees': out_deg,
            'connected': connected,
            'components': components,
            'has_cycle': has_cycle,
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Path Existence
# ─────────────────────────────────────────────

@app.route('/api/graph/path', methods=['POST'])
def check_path():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        src, dst = data['source'], data['target']
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        exists = nx.has_path(undirected, src, dst)
        path = nx.shortest_path(undirected, src, dst) if exists else []

        path_edges = list(zip(path, path[1:])) if path else []
        img = draw_graph(G, f"Path: {src} → {dst}",
                         highlight_nodes=set(path),
                         highlight_edges=set(path_edges))

        return jsonify({'success': True, 'exists': exists, 'path': path, 'image': img})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Eulerian
# ─────────────────────────────────────────────

@app.route('/api/graph/eulerian', methods=['POST'])
def eulerian():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        has_circuit = nx.is_eulerian(undirected)
        has_path = nx.has_eulerian_path(undirected)

        euler_path = []
        euler_type = "Not Eulerian"
        if has_circuit:
            euler_type = "Eulerian Circuit"
            euler_path = list(nx.eulerian_circuit(undirected))
        elif has_path:
            euler_type = "Eulerian Path"
            euler_path = list(nx.eulerian_path(undirected))

        odd_deg = [n for n in undirected.nodes() if undirected.degree(n) % 2 != 0]

        path_nodes = []
        if euler_path:
            path_nodes = [euler_path[0][0]] + [e[1] for e in euler_path]
        path_edges = set(euler_path)

        img = draw_graph(G, euler_type,
                         highlight_nodes=set(path_nodes) if path_nodes else None,
                         highlight_edges=path_edges)

        return jsonify({
            'success': True,
            'euler_type': euler_type,
            'path': path_nodes,
            'odd_degree_vertices': odd_deg,
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Hamiltonian
# ─────────────────────────────────────────────

def find_hamiltonian(G, path, visited, is_cycle=False):
    """Backtracking Hamiltonian path/cycle search."""
    if len(path) == G.number_of_nodes():
        if is_cycle:
            return G.has_edge(path[-1], path[0])
        return True
    for nbr in G.neighbors(path[-1]):
        if nbr not in visited:
            visited.add(nbr)
            path.append(nbr)
            if find_hamiltonian(G, path, visited, is_cycle):
                return True
            path.pop()
            visited.discard(nbr)
    return False


@app.route('/api/graph/hamiltonian', methods=['POST'])
def hamiltonian():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        nodes = list(undirected.nodes())
        ham_path = None
        ham_cycle = None

        # Try Hamiltonian Cycle
        for start in nodes:
            path = [start]
            visited = {start}
            if find_hamiltonian(undirected, path, visited, is_cycle=True):
                ham_cycle = path + [path[0]]
                break

        # Try Hamiltonian Path
        for start in nodes:
            path = [start]
            visited = {start}
            if find_hamiltonian(undirected, path, visited, is_cycle=False):
                ham_path = path
                break

        result_path = ham_cycle if ham_cycle else ham_path
        result_type = "Hamiltonian Cycle" if ham_cycle else ("Hamiltonian Path" if ham_path else "None Found")

        path_edges = set(zip(result_path, result_path[1:])) if result_path else set()
        img = draw_graph(G, result_type,
                         highlight_nodes=set(result_path) if result_path else None,
                         highlight_edges=path_edges)

        return jsonify({
            'success': True,
            'has_cycle': ham_cycle is not None,
            'has_path': ham_path is not None,
            'cycle': ham_cycle,
            'path': ham_path,
            'result_type': result_type,
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Shortest Path (Dijkstra)
# ─────────────────────────────────────────────

@app.route('/api/graph/shortest', methods=['POST'])
def shortest_path():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', True))
        src, dst = data['source'], data['target']

        weight = 'weight' if nx.is_weighted(G) else None
        path = nx.dijkstra_path(G, src, dst, weight=weight)
        length = nx.dijkstra_path_length(G, src, dst, weight=weight)

        path_edges = set(zip(path, path[1:]))
        img = draw_graph(G, f"Shortest Path: {src} → {dst}",
                         highlight_nodes=set(path),
                         highlight_edges=path_edges)

        return jsonify({
            'success': True,
            'path': path,
            'distance': length,
            'path_str': ' → '.join(path),
            'image': img
        })
    except nx.NetworkXNoPath:
        return jsonify({'success': False, 'error': f'No path between {data["source"]} and {data["target"]}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Graph Coloring
# ─────────────────────────────────────────────

@app.route('/api/graph/coloring', methods=['POST'])
def graph_coloring():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        color_map = nx.coloring.greedy_color(undirected, strategy='largest_first')
        num_colors = max(color_map.values()) + 1

        color_names = ['Red','Blue','Green','Yellow','Purple',
                       'Cyan','Pink','Lime','Orange','Teal']
        named_colors = {n: color_names[c % len(color_names)] for n, c in color_map.items()}

        img = draw_graph(G, f"Graph Coloring (χ = {num_colors} colors)", color_map=color_map)

        return jsonify({
            'success': True,
            'coloring': named_colors,
            'chromatic_number': num_colors,
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Planar Check
# ─────────────────────────────────────────────

@app.route('/api/graph/planar', methods=['POST'])
def planar_check():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        is_planar, _ = nx.check_planarity(undirected)
        img = draw_graph(G, f"Planar Graph: {'Yes ✓' if is_planar else 'No ✗'}")

        # Euler's formula info
        V = undirected.number_of_nodes()
        E = undirected.number_of_edges()
        euler_check = E <= 3*V - 6 if V >= 3 else True

        return jsonify({
            'success': True,
            'is_planar': is_planar,
            'vertices': V,
            'edges': E,
            'euler_formula': f"E ({E}) ≤ 3V-6 ({3*V-6}) : {'✓' if euler_check else '✗'}",
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Articulation Points
# ─────────────────────────────────────────────

@app.route('/api/graph/articulation', methods=['POST'])
def articulation_points():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        art_points = list(nx.articulation_points(undirected))
        bridges = list(nx.bridges(undirected))

        img = draw_graph(G, "Articulation Points (highlighted)",
                         highlight_nodes=set(art_points))

        return jsonify({
            'success': True,
            'articulation_points': art_points,
            'bridges': [list(b) for b in bridges],
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Biconnected Components
# ─────────────────────────────────────────────

@app.route('/api/graph/biconnected', methods=['POST'])
def biconnected():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        undirected = G.to_undirected() if isinstance(G, nx.DiGraph) else G

        components = list(nx.biconnected_components(undirected))
        img = draw_graph(G, f"Biconnected Components: {len(components)}")

        return jsonify({
            'success': True,
            'num_components': len(components),
            'components': [list(c) for c in components],
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Graph Isomorphism
# ─────────────────────────────────────────────

@app.route('/api/graph/isomorphism', methods=['POST'])
def isomorphism():
    try:
        data = request.json
        G1 = parse_graph_input(data['vertices1'], data['edges1'])
        G2 = parse_graph_input(data['vertices2'], data['edges2'])

        result = nx.is_isomorphic(G1, G2)

        img1 = draw_graph(G1, "Graph 1")
        img2 = draw_graph(G2, "Graph 2")

        return jsonify({
            'success': True,
            'isomorphic': result,
            'g1_nodes': G1.number_of_nodes(),
            'g1_edges': G1.number_of_edges(),
            'g2_nodes': G2.number_of_nodes(),
            'g2_edges': G2.number_of_edges(),
            'image1': img1,
            'image2': img2
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Subgraph
# ─────────────────────────────────────────────

@app.route('/api/graph/subgraph', methods=['POST'])
def subgraph():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'],
                              data.get('directed', False), data.get('weighted', False))
        sub_nodes = data['sub_nodes'].strip().split()
        SG = G.subgraph(sub_nodes)
        img = draw_graph(SG, f"Subgraph of {sub_nodes}")
        return jsonify({'success': True, 'image': img,
                        'edges': list(SG.edges())})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Tree Analysis
# ─────────────────────────────────────────────

@app.route('/api/tree/analyze', methods=['POST'])
def tree_analyze():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'], directed=False)

        if not nx.is_tree(G):
            return jsonify({'success': False,
                            'error': 'Input is not a valid tree (must be connected and acyclic).'})

        root = data.get('root', list(G.nodes())[0])
        T = nx.dfs_tree(G, root)

        leaves = [n for n in T.nodes() if T.out_degree(n) == 0 and n != root]
        internal = [n for n in T.nodes() if T.out_degree(n) > 0]
        height = nx.dag_longest_path_length(T)

        parents = {n: list(T.predecessors(n))[0] if list(T.predecessors(n)) else None
                   for n in T.nodes()}
        children = {n: list(T.successors(n)) for n in T.nodes()}

        # Draw tree
        fig, ax = plt.subplots(figsize=(9, 6))
        fig.patch.set_facecolor('#0f1117')
        ax.set_facecolor('#0f1117')

        try:
            from networkx.drawing.nx_agraph import graphviz_layout
            pos = graphviz_layout(T, prog='dot')
        except Exception:
            pos = nx.spring_layout(T, seed=42, k=3)

        node_colors = []
        for n in T.nodes():
            if n == root:
                node_colors.append('#f59e0b')
            elif n in leaves:
                node_colors.append('#22c55e')
            else:
                node_colors.append('#3b82f6')

        nx.draw_networkx_nodes(T, pos, node_color=node_colors, node_size=800, ax=ax)
        nx.draw_networkx_labels(T, pos, font_color='white', font_weight='bold', ax=ax)
        nx.draw_networkx_edges(T, pos, edge_color='#64748b', width=2, ax=ax,
                               arrows=True, arrowsize=15)

        legend = [mpatches.Patch(color='#f59e0b', label='Root'),
                  mpatches.Patch(color='#3b82f6', label='Internal'),
                  mpatches.Patch(color='#22c55e', label='Leaf')]
        ax.legend(handles=legend, loc='upper right',
                  facecolor='#1e293b', labelcolor='white', fontsize=9)
        ax.set_title("Tree Visualization", color='white', fontsize=14, fontweight='bold')
        ax.axis('off')
        img = fig_to_base64(fig)

        return jsonify({
            'success': True,
            'root': root,
            'leaves': leaves,
            'internal_nodes': internal,
            'height': height,
            'parents': parents,
            'children': children,
            'num_nodes': G.number_of_nodes(),
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Huffman Coding
# ─────────────────────────────────────────────

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman(chars_freqs):
    heap = [HuffmanNode(c, f) for c, f in chars_freqs]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)

    return heap[0] if heap else None


def get_codes(node, prefix="", codes=None):
    if codes is None:
        codes = {}
    if node is None:
        return codes
    if node.char is not None:
        codes[node.char] = prefix or "0"
    else:
        get_codes(node.left, prefix + "0", codes)
        get_codes(node.right, prefix + "1", codes)
    return codes


def draw_huffman_tree(root):
    """Draw Huffman tree."""
    G = nx.DiGraph()
    labels = {}
    node_id = [0]

    def add_nodes(node, parent=None, edge_label=""):
        nid = node_id[0]
        node_id[0] += 1
        label = f"{node.char}\n{node.freq}" if node.char else str(node.freq)
        labels[nid] = label
        G.add_node(nid)
        if parent is not None:
            G.add_edge(parent, nid, label=edge_label)
        if node.left:
            add_nodes(node.left, nid, "0")
        if node.right:
            add_nodes(node.right, nid, "1")

    add_nodes(root)

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#0f1117')

    try:
        from networkx.drawing.nx_agraph import graphviz_layout
        pos = graphviz_layout(G, prog='dot')
    except Exception:
        pos = nx.spring_layout(G, seed=42, k=2)

    leaf_ids = [n for n in G.nodes() if G.out_degree(n) == 0]
    colors = ['#22c55e' if n in leaf_ids else '#3b82f6' for n in G.nodes()]

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=900, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=labels,
                            font_color='white', font_size=8, font_weight='bold', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='#64748b', width=2,
                           arrows=True, arrowsize=12, ax=ax)

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_color='#f59e0b', font_size=10, ax=ax)

    ax.set_title("Huffman Tree", color='white', fontsize=14, fontweight='bold')
    ax.axis('off')
    return fig_to_base64(fig)


@app.route('/api/tree/huffman', methods=['POST'])
def huffman():
    try:
        data = request.json
        lines = data['input'].strip().splitlines()
        chars_freqs = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 2:
                raise ValueError(f"Each line must be 'char freq', got: '{line}'")
            chars_freqs.append((parts[0], int(parts[1])))

        root = build_huffman(chars_freqs)
        codes = get_codes(root)
        img = draw_huffman_tree(root)

        total_bits = sum(freq * len(codes[char]) for char, freq in chars_freqs)
        avg_bits = total_bits / sum(f for _, f in chars_freqs)

        return jsonify({
            'success': True,
            'codes': codes,
            'total_bits': total_bits,
            'avg_bits': round(avg_bits, 4),
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ─────────────────────────────────────────────
# API: Map Coloring
# ─────────────────────────────────────────────

@app.route('/api/graph/mapcolor', methods=['POST'])
def map_color():
    try:
        data = request.json
        G = parse_graph_input(data['vertices'], data['edges'])
        color_map = nx.coloring.greedy_color(G, strategy='largest_first')
        num_colors = max(color_map.values()) + 1

        color_names = ['Red','Blue','Green','Yellow','Purple','Cyan']
        named = {n: color_names[c % len(color_names)] for n, c in color_map.items()}

        img = draw_graph(G, f"Map Coloring ({num_colors} colors)", color_map=color_map)

        return jsonify({
            'success': True,
            'coloring': named,
            'num_colors': num_colors,
            'image': img
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
