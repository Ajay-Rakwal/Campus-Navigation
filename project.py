import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import heapq

# ==============================
# Database
# ==============================
def connect_db():
    """Create and return a MySQL connection. Adjust password if needed."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # <--- set if needed
        database="campus_navigator"
    )

# ==============================
# Graph Algorithms
# ==============================
def a_star(graph: dict, start: str, goal: str):
    """
    A* without heuristic (acts like Dijkstra on this small graph).
    Returns (path_nodes_list or None, total_cost).
    """
    pq = [(0, start)]
    came_from = {}
    cost = {start: 0}
    while pq:
        _, u = heapq.heappop(pq)
        if u == goal:
            break
        for v, w in graph[u].items():
            nd = cost[u] + w
            if v not in cost or nd < cost[v]:
                cost[v] = nd
                came_from[v] = u
                heapq.heappush(pq, (nd, v))
    if start == goal:
        return [start], 0
    if goal not in came_from:
        return None, float('inf')
    # reconstruct
    path, cur = [], goal
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.append(start)
    path.reverse()
    return path, cost[goal]

def dijkstra_spt(graph: dict, start: str):
    """
    Dijkstra shortest-path tree from start.
    Returns (dist: dict[node->cost], parent: dict[node->parent]).
    """
    dist = {u: float('inf') for u in graph}
    parent = {u: None for u in graph}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, parent

def _find(parent, x):
    if parent[x] != x:
        parent[x] = _find(parent, parent[x])
    return parent[x]

def _union(parent, rank, a, b):
    ra, rb = _find(parent, a), _find(parent, b)
    if ra == rb:
        return
    if rank[ra] < rank[rb]:
        parent[ra] = rb
    elif rank[ra] > rank[rb]:
        parent[rb] = ra
    else:
        parent[rb] = ra
        rank[ra] += 1

def kruskal_mst(graph: dict):
    """
    Kruskal MST for an undirected weighted graph (dict of dict).
    Returns (mst_edges: list[(u,v,w)], total_weight).
    """
    edges, seen = [], set()
    for u in graph:
        for v, w in graph[u].items():
            key = tuple(sorted((u, v)))
            if key in seen:
                continue
            seen.add(key)
            edges.append((w, u, v))
    edges.sort()
    parent, rank = {}, {}
    for u in graph:
        parent[u] = u
        rank[u] = 0
    mst, total = [], 0
    for w, u, v in edges:
        if _find(parent, u) != _find(parent, v):
            _union(parent, rank, u, v)
            mst.append((u, v, w))
            total += w
    return mst, total

# ==============================
# Data: Campus Graph + Positions
# ==============================
CAMPUS_GRAPH = {
    'Front Gate': {'Library': 2, 'Canteen': 4, 'Admin': 3},
    'Admin': {'Front Gate': 3, 'Library': 2, 'Auditorium': 4, 'Research Block': 5},
    'Library': {'Front Gate': 2, 'Admin': 2, 'Hostel': 3, 'Lab': 4, 'Research Block': 3},
    'Hostel': {'Library': 3, 'Lab': 2, 'Sports Complex': 5, 'Parking': 6},
    'Canteen': {'Front Gate': 4, 'Lab': 3, 'Cultural Center': 4},
    'Lab': {'Library': 4, 'Hostel': 2, 'Canteen': 3, 'Ground': 5, 'Auditorium': 6, 'Research Block': 4},
    'Ground': {'Lab': 5, 'Sports Complex': 3, 'Parking': 4, 'Back Gate': 4},
    'Sports Complex': {'Hostel': 5, 'Ground': 3, 'Parking': 2, 'Back Gate': 5},
    'Auditorium': {'Admin': 4, 'Lab': 6, 'Cultural Center': 2},
    'Cultural Center': {'Canteen': 4, 'Auditorium': 2, 'Parking': 5},
    'Parking': {'Ground': 4, 'Sports Complex': 2, 'Cultural Center': 5, 'Hostel': 6, 'Back Gate': 3},
    'Research Block': {'Library': 3, 'Lab': 4, 'Admin': 5},
    'Back Gate': {'Parking': 3, 'Ground': 4, 'Sports Complex': 5}
}

NODE_POS = {
    'Front Gate': (60, 180),
    'Admin': (170, 130),
    'Library': (250, 60),
    'Hostel': (420, 40),
    'Research Block': (330, 100),
    'Lab': (420, 180),
    'Canteen': (250, 300),
    'Ground': (550, 230),
    'Sports Complex': (620, 90),
    'Auditorium': (500, 130),
    'Cultural Center': (400, 330),
    'Parking': (620, 280),
    'Back Gate': (740, 200)
}

# ==============================
# UI Helper: Scrollable Frame (scrolls the entire page)
# ==============================
class ScrollablePage(tk.Frame):
    """
    A frame that makes all its child content scrollable vertically.
    Usage:
        page = ScrollablePage(root)
        page.pack(fill="both", expand=True)
        content = page.content   # put your actual UI into 'content'
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#D4E6F1")
        self._vbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vbar.set)

        self._vbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # A frame inside the canvas: put real content here
        self.content = tk.Frame(self._canvas, bg="#D4E6F1")
        self._window = self._canvas.create_window((0, 0), window=self.content, anchor="nw")

        # Update scroll region when content changes size
        self.content.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel support (Windows/macOS)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux (button 4/5)
        self._canvas.bind_all("<Button-4>", lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>", lambda e: self._canvas.yview_scroll(1, "units"))

    def _on_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # match content width to canvas width for nice page feel
        self._canvas.itemconfig(self._window, width=event.width)

    def _on_mousewheel(self, event):
        # On Windows, event.delta is multiples of 120
        delta = int(-1 * (event.delta / 120))
        self._canvas.yview_scroll(delta, "units")

# ==============================
# GUI App
# ==============================
class CampusNavigatorApp:
    """
    Tkinter GUI for:
      - MySQL login/sign-up
      - A* shortest path + Save/View routes
      - Kruskal MST view
      - Dijkstra reachability within budget
      - Entire window scrollable (via ScrollablePage)
    """

    # ---- Theme constants ----
    BG_MAIN = "#D4E6F1"
    BG_PANEL = "#AED6F1"
    NODE_FILL = "#2980B9"
    NODE_OUTLINE = "#1B4F72"
    NODE_REACHABLE = "#FFD54F"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Campus Navigator - Smart Path Finder")
        self.root.geometry("920x640")
        self.root.configure(bg=self.BG_MAIN)
        self.current_user = None
        self._build_login()

    # ---------------- Login ----------------
    def _build_login(self):
        """Build login/sign-up screen (also inside a scrollable page for consistency)."""
        for w in self.root.winfo_children():
            w.destroy()

        page = ScrollablePage(self.root)
        page.pack(fill="both", expand=True)
        container = page.content  # all UI goes here

        tk.Label(container, text="Campus Navigator Login", font=("Arial", 20, "bold"), bg=self.BG_MAIN).pack(pady=20)

        tk.Label(container, text="Username:", bg=self.BG_MAIN, font=("Arial", 12)).pack()
        entry_user = tk.Entry(container)
        entry_user.pack(pady=5)

        tk.Label(container, text="Password:", bg=self.BG_MAIN, font=("Arial", 12)).pack()
        entry_pass = tk.Entry(container, show="*")
        entry_pass.pack(pady=5)

        def do_login():
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                        (entry_user.get(), entry_pass.get()))
            row = cur.fetchone()
            conn.close()
            if row:
                self.current_user = entry_user.get()
                messagebox.showinfo("Success", "Login Successful!")
                self._build_main()
            else:
                messagebox.showerror("Error", "Invalid Credentials")

        def do_signup():
            conn = connect_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                            (entry_user.get(), entry_pass.get()))
                conn.commit()
                messagebox.showinfo("Success", "Account Created Successfully!")
            except:
                messagebox.showerror("Error", "Username already exists!")
            conn.close()

        tk.Button(container, text="Login", command=do_login, bg="#2980B9", fg="white", width=10).pack(pady=10)
        tk.Button(container, text="Sign Up", command=do_signup, bg="#27AE60", fg="white", width=10).pack(pady=5)
        tk.Button(container, text="Exit", command=self.root.quit, bg="#C0392B", fg="white", width=10).pack(pady=10)

    # ---------------- Main ----------------
    def _build_main(self):
        """Build main (map + controls) screen inside a scrollable page."""
        for w in self.root.winfo_children():
            w.destroy()

        page = ScrollablePage(self.root)
        page.pack(fill="both", expand=True)
        container = page.content  # all widgets attach here

        # Header
        tk.Label(container, text="Campus Navigator", font=("Arial", 20, "bold"),
                 bg=self.BG_MAIN).pack(pady=8)

        # Controls panel
        ctrl = tk.Frame(container, bg=self.BG_PANEL)
        ctrl.pack(pady=6, fill="x", padx=10)

        tk.Label(ctrl, text="Source:", bg=self.BG_PANEL).grid(row=0, column=0, padx=6, pady=8, sticky="e")
        self.src_var = tk.StringVar()
        ttk.Combobox(ctrl, textvariable=self.src_var, values=list(CAMPUS_GRAPH.keys())).grid(row=0, column=1, padx=6, pady=8)

        tk.Label(ctrl, text="Destination:", bg=self.BG_PANEL).grid(row=1, column=0, padx=6, pady=8, sticky="e")
        self.dst_var = tk.StringVar()
        ttk.Combobox(ctrl, textvariable=self.dst_var, values=list(CAMPUS_GRAPH.keys())).grid(row=1, column=1, padx=6, pady=8)

        tk.Label(ctrl, text="Budget Distance:", bg=self.BG_PANEL).grid(row=0, column=2, padx=6, pady=8, sticky="e")
        self.budget_var = tk.StringVar(value="8")
        tk.Entry(ctrl, textvariable=self.budget_var, width=10).grid(row=0, column=3, padx=6, pady=8)

        # Buttons row
        tk.Button(ctrl, text="Find Path (A*)", bg="#2980B9", fg="white", width=16,
                  command=self._on_find_path).grid(row=2, column=0, padx=6, pady=10)
        tk.Button(ctrl, text="Show MST", bg="#27AE60", fg="white", width=16,
                  command=self._on_show_mst).grid(row=2, column=1, padx=6, pady=10)
        tk.Button(ctrl, text="Within Budget (Dijkstra)", bg="#8e44ad", fg="white", width=20,
                  command=self._on_show_reachable).grid(row=2, column=2, padx=6, pady=10)

        # Results text
        self.result_label = tk.Label(container, text="", bg=self.BG_MAIN, font=("Arial", 12), justify="left")
        self.result_label.pack(pady=4, fill="x", padx=10)

        # Map Canvas (not scrollable by itself; page scrolls everything)
        map_frame = tk.Frame(container, bg=self.BG_MAIN)
        map_frame.pack(pady=6, padx=10, fill="x")
        self.map_canvas = tk.Canvas(map_frame, bg="white", width=880, height=400)
        self.map_canvas.pack()

        # Bottom bar: Logout + View Saved Routes (always visible in page)
        bottom = tk.Frame(container, bg=self.BG_MAIN)
        bottom.pack(pady=10)
        tk.Button(bottom, text="Logout", command=self._build_login, bg="#C0392B", fg="white", width=12).pack(side="left", padx=6)
        tk.Button(bottom, text="📋 View Saved Routes", command=self._on_view_saved_routes,
                  bg="#3498db", fg="white", width=18).pack(side="left", padx=6)

        # Initial draw
        self._draw_map()

    # ==============================
    # Drawing
    # ==============================
    def _node_bbox(self, name: str, x: int, y: int):
        """Compute ellipse bounds based on name length so text fits nicely."""
        half_w = max(25, 10 + 4 * len(name))   # horizontal radius grows with label length
        half_h = 18                             # vertical radius (constant looks good)
        return (x - half_w, y - half_h, x + half_w, y + half_h)

    def _draw_map(self, path=None, mst=None, spt=None, reachable=None):
        """
        Draw the whole map:
          - Gray edges (+weights)
          - Optional MST edges (green)
          - Optional SPT edges (orange) and reachable nodes (yellow)
          - Optional path (blue) for A*
        """
        c = self.map_canvas
        c.delete("all")

        # Base edges + weights
        drawn = set()
        for u in CAMPUS_GRAPH:
            for v, w in CAMPUS_GRAPH[u].items():
                key = tuple(sorted((u, v)))
                if key in drawn:
                    continue
                drawn.add(key)
                x1, y1 = NODE_POS[u]
                x2, y2 = NODE_POS[v]
                c.create_line(x1, y1, x2, y2, fill="gray", width=1)
                c.create_text((x1 + x2)//2, (y1 + y2)//2, text=str(w), font=("Arial", 8))

        # MST (green)
        if mst:
            for u, v, _ in mst:
                x1, y1 = NODE_POS[u]
                x2, y2 = NODE_POS[v]
                c.create_line(x1, y1, x2, y2, fill="green", width=3)

        # SPT (orange)
        if spt:
            for u, v in spt:
                x1, y1 = NODE_POS[u]
                x2, y2 = NODE_POS[v]
                c.create_line(x1, y1, x2, y2, fill="#ff8c00", width=3)

        # Path (blue) + direction arrow
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                a, b = path[i], path[i + 1]
                if a in NODE_POS and b in NODE_POS:
                    x1, y1 = NODE_POS[a]
                    x2, y2 = NODE_POS[b]
                    c.create_line(x1, y1, x2, y2, fill="blue", width=3)
                    # small arrow
                    dx, dy = x2 - x1, y2 - y1
                    L = (dx*dx + dy*dy) ** 0.5
                    if L:
                        ux, uy = dx / L, dy / L
                        ax, ay = x1 + 0.7 * dx, y1 + 0.7 * dy
                        s = 8
                        c.create_polygon(
                            ax, ay,
                            ax - uy * s + ux * s / 2, ay + ux * s + uy * s / 2,
                            ax + uy * s + ux * s / 2, ay - ux * s + uy * s / 2,
                            fill="blue"
                        )

        # Nodes (reachable yellow else blue)
        reach = set(reachable) if reachable else set()
        for name, (x, y) in NODE_POS.items():
            x0, y0, x1, y1 = self._node_bbox(name, x, y)
            fill = self.NODE_REACHABLE if name in reach else self.NODE_FILL
            c.create_oval(x0, y0, x1, y1, fill=fill, outline=self.NODE_OUTLINE, width=2)
            c.create_text(x, y, text=name, fill="white", font=("Arial", 10, "bold"))

    # ==============================
    # Actions
    # ==============================
    def _on_find_path(self):
        """Compute A* path using selected source/destination, draw + offer to save."""
        start, goal = self.src_var.get(), self.dst_var.get()
        if not start or not goal:
            messagebox.showwarning("Warning", "Please select both source and destination!")
            return
        path, cost = a_star(CAMPUS_GRAPH, start, goal)
        if not path:
            self.result_label.config(text="No Path Found!")
            self._draw_map()
            return
        self._draw_map(path=path)
        route_text = " -> ".join(path)
        self.result_label.config(text=f"Shortest Path (A*): {route_text}\nTotal Distance: {cost}")
        # Small save button below results (stays in scrollable page)
        tk.Button(self.result_label.master, text="💾 Save Route", bg="#2ecc71", fg="white",
                  command=lambda: self._save_route(start, goal, route_text)).pack(pady=4)

    def _on_show_mst(self):
        """Build and draw MST (Kruskal)."""
        mst, total = kruskal_mst(CAMPUS_GRAPH)
        self._draw_map(mst=mst)
        edges_text = "\n".join([f"{u} - {v} ({w})" for u, v, w in mst])
        messagebox.showinfo("Minimum Spanning Tree",
                            f"{edges_text}\n\nTotal Weight: {total}")

    def _on_show_reachable(self):
        """Dijkstra reachability: show nodes within the given budget from Source."""
        start = self.src_var.get()
        if not start:
            messagebox.showwarning("Warning", "Select a starting location for reachability!")
            return
        try:
            budget = float(self.budget_var.get())
            if budget < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Input", "Enter a valid non-negative budget.")
            return

        dist, parent = dijkstra_spt(CAMPUS_GRAPH, start)
        reachable = sorted([u for u, d in dist.items() if d <= budget], key=lambda x: dist[x])

        # Collect SPT edges only for nodes that are actually reachable
        spt_edges = []
        for u in reachable:
            if parent[u] is not None:
                spt_edges.append((parent[u], u))

        self._draw_map(spt=spt_edges, reachable=reachable)
        if reachable:
            listing = "\n".join([f"• {u} (dist {dist[u]})" for u in reachable])
            self.result_label.config(text=f"Reachable within {budget} from {start}:\n{listing}")
        else:
            self.result_label.config(text=f"No locations reachable within {budget} from {start}.")

    # ==============================
    # Saved Routes (SQL)
    # ==============================
    def _ensure_saved_routes_table(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS saved_routes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50),
                source VARCHAR(50),
                destination VARCHAR(50),
                route_text TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _save_route(self, source: str, destination: str, route_text: str):
        """Save the current route to MySQL."""
        try:
            self._ensure_saved_routes_table()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO saved_routes (username, source, destination, route_text)
                VALUES (%s, %s, %s, %s)
            """, (self.current_user, source, destination, route_text))
            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Route saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_view_saved_routes(self):
        """Show a scrollable list of saved routes for the current user."""
        try:
            self._ensure_saved_routes_table()
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                SELECT source, destination, route_text, saved_at
                FROM saved_routes
                WHERE username=%s
                ORDER BY saved_at DESC
            """, (self.current_user,))
            rows = cur.fetchall()
            conn.close()

            win = tk.Toplevel(self.root)
            win.title("📋 Saved Routes")
            win.geometry("540x420")
            win.configure(bg="#121212")

            tk.Label(win, text=f"Saved Routes for {self.current_user}",
                     fg="#00ffcc", bg="#121212", font=("Segoe UI", 12, "bold")).pack(pady=10)

            # Scrollable area
            container = tk.Frame(win, bg="#121212")
            container.pack(fill="both", expand=True)

            list_canvas = tk.Canvas(container, bg="#121212", highlightthickness=0)
            ybar = ttk.Scrollbar(container, orient="vertical", command=list_canvas.yview)
            list_canvas.configure(yscrollcommand=ybar.set)

            ybar.pack(side="right", fill="y")
            list_canvas.pack(side="left", fill="both", expand=True)

            list_frame = tk.Frame(list_canvas, bg="#121212")
            list_canvas.create_window((0, 0), window=list_frame, anchor="nw")

            def _on_config(_):
                list_canvas.configure(scrollregion=list_canvas.bbox("all"))
            list_frame.bind("<Configure>", _on_config)

            if not rows:
                tk.Label(list_frame, text="No routes saved yet!",
                         fg="white", bg="#121212", font=("Arial", 10)).pack(pady=20)
            else:
                for idx, (src, dst, path, when) in enumerate(rows, 1):
                    tk.Label(
                        list_frame,
                        text=f"{idx}. {src} → {dst}\n🕓 {when}\nPath: {path}",
                        fg="white", bg="#1f1f1f",
                        anchor="w", justify="left",
                        font=("Consolas", 9), padx=10, pady=6
                    ).pack(fill="x", pady=4, padx=6)

        except Exception as e:
            messagebox.showerror("Error", str(e))

# ==============================
# Run
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = CampusNavigatorApp(root)
    root.mainloop()
