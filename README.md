<<<<<<< HEAD
# Graph and Tree Analysis Toolkit
### Discrete Mathematics Project — B.Tech CSE (AI & ML)

A complete interactive web application for graph theory and tree analysis using Python Flask, NetworkX, and Matplotlib.

---

## Features

| Module | Description |
|--------|-------------|
| Graph Properties | Degree, connectivity, components, cycle detection |
| Path Existence | Check if path exists between two vertices |
| Subgraph | Extract induced subgraph |
| Eulerian Walk | Detect Euler circuit/path using Hierholzer's algorithm |
| Hamiltonian Path | Detect Hamilton path/cycle via backtracking |
| Shortest Path | Dijkstra's algorithm with visual highlight |
| Graph Coloring | Greedy vertex coloring, chromatic number |
| Map Coloring | Region coloring using graph coloring |
| Planar Graph | Planarity check (Boyer–Myrvold) |
| Articulation Points | Cut vertices and bridges (Tarjan's) |
| Biconnected Components | Count and list components |
| Graph Isomorphism | VF2 isomorphism testing |
| Tree Analysis | Root, leaves, height, parent/child info |
| Huffman Coding | Build optimal prefix codes with visualization |

---

## Project Structure

```
graph-toolkit/
├── app.py              # Flask backend with all API endpoints
├── requirements.txt    # Python dependencies
├── README.md
└── templates/
    ├── base.html       # Base template with navigation
    ├── index.html      # Home page
    ├── about.html      # Theory & About page
    ├── tools.html      # Graph tools page
    └── tree.html       # Tree tools page
```

---

## Installation & Setup

### Step 1: Clone / Extract the project
```bash
cd graph-toolkit
```

### Step 2: Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the application
```bash
python app.py
```

### Step 5: Open in browser
```
http://localhost:5000
```

---

## Example Inputs

### Graph Properties
```
Vertices: A B C D E
Edges:
A-B
B-C
C-D
D-A
A-E
```

### Weighted Graph (Shortest Path)
```
Vertices: A B C D E
Edges:
A-B 4
B-C 3
C-D 2
A-D 10
B-D 5
Source: A    Target: D
```

### Eulerian Walk
```
Vertices: A B C D E
Edges:
A-B
B-C
C-D
D-A
A-E
E-C
```
(Result: Eulerian Path — exactly 2 odd-degree vertices)

### Huffman Coding
```
A 5
B 9
C 12
D 13
E 16
F 45
```

### Tree Analysis
```
Vertices: A B C D E F G
Edges:
A-B
A-C
B-D
B-E
C-F
C-G
Root: A
```

---

## Technologies Used

- **Backend:** Python 3.x, Flask 3.0
- **Graph Engine:** NetworkX 3.3
- **Visualization:** Matplotlib 3.9
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Design:** Custom CSS with CSS variables, Google Fonts

---

## Notes

- All graph algorithms are mathematically correct per Discrete Mathematics theory
- Hamiltonian path uses backtracking (NP-complete, works for small graphs)
- Eulerian detection uses Hierholzer's algorithm (O(E))
- Dijkstra works only on non-negative weighted graphs
- Planarity uses Boyer–Myrvold O(V) algorithm
=======

