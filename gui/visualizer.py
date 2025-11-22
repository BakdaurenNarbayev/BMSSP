# visualizer.py
import os
import tempfile
import random
from typing import Optional, Dict, Any

import networkx as nx
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from textual.widgets import Static


class GraphVisualizer(Static):
    """Widget to display graph visualization as an image"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph = None
        self.nx_graph = None
        self.result = None
        self.path = None
        self.start = None
        self.end = None
        self.graph_name = ""
        self.image_path: Optional[str] = None

    def set_graph(self, graph, start, end, seed, graph_name: str = ""):
        """Set the graph to display"""
        self.graph = graph
        self.start = start
        self.end = end
        self.result = None
        self.path = None
        self.graph_name = graph_name

        # Convert to NetworkX directed graph
        self.nx_graph = nx.DiGraph()
        for node in range(graph.node_count):
            self.nx_graph.add_node(node)

        # Add directed edges from adjacency list
        for from_node, neighbors in graph.adjacency_list.items():
            for to_node, weight in neighbors:
                self.nx_graph.add_edge(from_node, to_node, weight=weight)

        self.generate_image(seed)

    def set_result(self, result, start, end, seed):
        """Set the algorithm result and regenerate with path"""
        self.result = result
        try:
            self.path = result.get_path(start, end) if result else None
        except Exception:
            self.path = None
        self.generate_image(seed)

    def generate_image(self, seed):
        """Generate the graph visualization image"""
        if not self.nx_graph:
            self.update("No graph loaded.")
            return

        fig, ax = plt.subplots(figsize=(12, 9), facecolor="white")
        ax.set_facecolor("white")
        ax.axis("off")

        # Node colors/sizes
        node_colors = []
        node_sizes = []
        for node in self.nx_graph.nodes():
            if node == self.start:
                node_colors.append("#00aa00")
                node_sizes.append(1000)
            elif node == self.end:
                node_colors.append("#dd0000")
                node_sizes.append(1000)
            elif self.path and node in self.path:
                node_colors.append("#ff8800")
                node_sizes.append(700)
            else:
                node_colors.append("#4488ff")
                node_sizes.append(500)

        # Edge style and path edges
        edge_colors = []
        edge_widths = []
        path_edges = set()
        if self.path:
            for i in range(len(self.path) - 1):
                path_edges.add((self.path[i], self.path[i + 1]))

        for edge in self.nx_graph.edges():
            if edge in path_edges:
                edge_colors.append("#ff8800")
                edge_widths.append(4.0)
            else:
                edge_colors.append("#000000")
                edge_widths.append(1.5)

        pos = nx.spring_layout(self.nx_graph, k=1, seed=seed)

        nx.draw_networkx_edges(
            self.nx_graph,
            pos,
            edge_color=edge_colors,
            width=edge_widths,
            ax=ax,
            arrows=True,
            arrowsize=20,
            arrowstyle="-|>",
            node_size=node_sizes,
            connectionstyle="arc3",
        )

        edge_labels = nx.get_edge_attributes(self.nx_graph, "weight")
        edge_labels = {k: f"{int(v)}" for k, v in edge_labels.items()}

        path_edge_labels = {k: v for k, v in edge_labels.items() if k in path_edges}
        other_edge_labels = {
            k: v for k, v in edge_labels.items() if k not in path_edges
        }

        if other_edge_labels:
            nx.draw_networkx_edge_labels(
                self.nx_graph,
                pos,
                other_edge_labels,
                font_size=9,
                font_color="#333333",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor="#cccccc",
                    alpha=0.8,
                ),
                ax=ax,
            )

        if path_edge_labels:
            nx.draw_networkx_edge_labels(
                self.nx_graph,
                pos,
                path_edge_labels,
                font_size=10,
                font_color="#ff8800",
                font_weight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="#fff5e6",
                    edgecolor="#ff8800",
                    alpha=0.9,
                ),
                ax=ax,
            )

        nx.draw_networkx_nodes(
            self.nx_graph,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors="#333333",
            linewidths=2,
            ax=ax,
        )

        labels = {}
        for node in self.nx_graph.nodes():
            if node == self.start:
                labels[node] = f"S({node})"
            elif node == self.end:
                labels[node] = f"E({node})"
            else:
                labels[node] = str(node)

        nx.draw_networkx_labels(
            self.nx_graph,
            pos,
            labels,
            font_size=10,
            font_color="white",
            font_weight="bold",
            ax=ax,
        )

        title = self.graph_name or ""
        if self.result and self.path:
            dist = self.result.get_distance(self.end)
            dist_str = f"{int(dist)}" if dist == int(dist) else f"{dist:.2f}"
            title += f"\nShortest Path Distance: {dist_str} | Path Length: {len(self.path) - 1} edges"
        ax.set_title(title, color="#000000", fontsize=16, pad=20, fontweight="bold")

        # Legend
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#00aa00",
                markersize=12,
                label="Start Node",
                markeredgecolor="#333333",
                markeredgewidth=2,
            ),
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#dd0000",
                markersize=12,
                label="End Node",
                markeredgecolor="#333333",
                markeredgewidth=2,
            ),
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#ff8800",
                markersize=10,
                label="Path Nodes",
                markeredgecolor="#333333",
                markeredgewidth=2,
            ),
            plt.Line2D([0], [0], color="#ff8800", linewidth=4, label="Path Edges"),
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="#4488ff",
                markersize=8,
                label="Other Nodes",
                markeredgecolor="#333333",
                markeredgewidth=2,
            ),
            plt.Line2D([0], [0], color="#666666", linewidth=1.5, label="Other Edges"),
        ]
        ax.legend(
            handles=legend_elements,
            fontsize=9,
            framealpha=0.9,
            edgecolor="#333333",
        )

        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except Exception:
                pass

        self.image_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        plt.savefig(
            self.image_path,
            facecolor="white",
            edgecolor="none",
            dpi=150,
            bbox_inches="tight",
            pad_inches=0.2,
        )
        plt.close(fig)

        # Display textual summary
        try:
            img = PILImage.open(self.image_path)
            width, height = img.size

            info = []
            info.append("=" * 70)
            info.append(f"GRAPH VISUALIZATION: {self.graph_name}")
            info.append("=" * 70)
            info.append("")
            info.append(f"Graph Properties:")
            info.append(f"   • Nodes: {self.graph.node_count}")
            info.append(f"   • Directed Edges: {self.graph.edge_count}")
            info.append(f"   • Start Node: {self.start}")
            info.append(f"   • End Node: {self.end}")
            info.append("")
            info.append(f"Legend:")
            info.append(f"   🟢 Green = Start Node (S)")
            info.append(f"   🔴 Red = End Node (E)")
            info.append(f"   🟠 Orange = Shortest Path (nodes & edges)")
            info.append(f"   🔵 Blue = Other Nodes")
            info.append(f"   ⚫ Gray = Other Edges")
            info.append(f"   📝 Numbers on edges = Edge weights")
            info.append(f"   ➡️  Arrows show edge direction")
            info.append("")

            if self.result:
                info.append("─" * 70)
                info.append("ALGORITHM RESULTS")
                info.append("─" * 70)
                if self.path:
                    path_str = " → ".join(str(n) for n in self.path)
                    info.append(f"Shortest Path Found:")
                    info.append(f"   {path_str}")
                    info.append("")
                    dist = self.result.get_distance(self.end)
                    dist_str = f"{int(dist)}" if dist == int(dist) else f"{dist:.2f}"
                    info.append(f"   Distance: {dist_str}")
                    info.append(f"   Path Length: {len(self.path) - 1} edges")
                    info.append(f"   Algorithm: {self.result.algorithm}")
                    info.append(
                        f"   Execution Time: {self.result.execution_time * 1000:.3f} ms"
                    )
                    info.append(f"   Operations: {self.result.operations:,}")
                else:
                    info.append("No path exists between start and end nodes")

            info.append("")
            info.append("─" * 70)
            info.append(f"Image File: {self.image_path}")
            info.append(f"Image Size: {width} x {height} pixels")
            info.append(f"Tip: Press 'o' or click 'Open Image' to view in image viewer")
            info.append("=" * 70)

            self.update("\n".join(info))

        except Exception as e:
            self.update(f"Error displaying image: {str(e)}")

    def cleanup(self):
        """Remove temporary image file"""
        if self.image_path and os.path.exists(self.image_path):
            try:
                os.remove(self.image_path)
            except Exception:
                pass
