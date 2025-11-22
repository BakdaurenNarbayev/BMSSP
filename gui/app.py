import os
import re
import random
import asyncio

from widgets import StatsDisplay
from visualizer import GraphVisualizer
from textual.app import App, ComposeResult
from sample_graphs import GRAPH_SIZES, create_sample_graphs
from graph_algorithms import dijkstra, bellman_ford
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Button, Select, Label, Static


class PathfindingTUI(App):
    CSS = """
    Screen {
        background: $surface;
    }
    #controls {
        dock: top;
        height: auto;
        background: $panel;
        padding: 1 2;
    }
    #main-container {
        height: 100%;
        layout: horizontal;
    }
    #graph-panel {
        width: 2fr;
        height: 100%;
        border: solid $primary;
        padding: 1 2;
        background: $surface;
    }
    #side-panel {
        width: 1fr;
        height: 100%;
        layout: vertical;
        border: solid $primary;
        background: $panel;
    }
    #stats {
        height: auto;
        padding: 1 2;
        border-bottom: solid $primary;
    }
    #status {
        height: auto;
        padding: 1 2;
        background: $surface;
    }
    Button { margin: 0 1; }
    Select { width: 1fr; margin: 0 1; }
    Label { padding: 0 1; color: $text; }
    .control-row { height: auto; layout: horizontal; padding: 0 0 1 0; }
    GraphVisualizer { height: 100%; overflow-y: auto; }
    #info-panel { padding: 1 2; background: $surface; height: auto; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "run", "Run Algorithm"),
        ("g", "gen", "Generate New Graph"),
        ("o", "open_image", "Open Image"),
    ]

    def __init__(self):
        super().__init__()
        self.graphs = list(GRAPH_SIZES.keys())
        self.current_graph = None
        self.current_graph_key = None
        self.current_graph_info = None
        self.current_algorithm = None
        self.seed = self.get_random_seed()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="controls"):
            with Horizontal(classes="control-row"):
                yield Label("Graph:")
                yield Select(
                    options=[
                        ((f"{msg} ({nodes}x{nodes} DAG)", key))
                        for key, (nodes, msg) in GRAPH_SIZES.items()
                    ],
                    id="graph-select",
                    value="xs",
                )
                yield Label("Algorithm:")
                yield Select(
                    options=[
                        ("Dijkstra's Algorithm", "dijkstra"),
                        ("Bellman-Ford Algorithm", "bellman_ford"),
                    ],
                    id="algo-select",
                    value="dijkstra",
                )

            with Horizontal(classes="control-row"):
                yield Button("Run Algorithm", variant="primary", id="run-btn")
                yield Button("Generate New Graph", variant="default", id="gen-btn")
                yield Button("Open Image", variant="default", id="open-btn")

        with Container(id="main-container"):
            with ScrollableContainer(id="graph-panel"):
                yield GraphVisualizer(id="graph-display")

            with Vertical(id="side-panel"):
                yield StatsDisplay(id="stats")
                with Container(id="status"):
                    yield Static("", id="status-text")
                with Container(id="info-panel"):
                    yield Static("", id="info-text")

        yield Footer()

    def load_graph(self, graph_key):
        if graph_key in self.graphs:
            self.seed = self.get_random_seed()
            graph, start, end, description = create_sample_graphs(graph_key, self.seed)
            self.current_graph = graph
            self.current_graph_info = (start, end, description)

            display = self.query_one("#graph-display", GraphVisualizer)
            display.set_graph(graph, start, end, self.seed, description)

            stats = self.query_one("#stats", StatsDisplay)
            stats.update_stats()

            cleaned_description = re.sub(r"\(\d+\s+nodes\)", "", description).strip()
            self.update_status(
                f"Loaded: {cleaned_description} ({graph.node_count} nodes, {graph.edge_count} edges)"
            )

    def update_status(self, message: str):
        status_widget = self.query_one("#status-text", Static)
        previous_status = status_widget.content or ""

        info_widget = self.query_one("#info-text", Static)
        history = info_widget.content or ""

        if previous_status:
            new_info = f"{previous_status}\n{history}" if history else previous_status
            info_widget.update(new_info)

        status_widget.update(message)

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "graph-select":
            self.current_graph_key = event.value
            self.load_graph(self.current_graph_key)
        elif event.select.id == "algo-select":
            self.current_algorithm = event.value

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-btn":
            await self.run_algorithm()
        elif event.button.id == "gen-btn":
            self.action_gen()
        elif event.button.id == "open-btn":
            self.action_open_image()

    async def run_algorithm(self):
        if not self.current_graph or not self.current_graph_info:
            self.update_status("Please select a graph first!")
            return

        algo_select = self.query_one("#algo-select", Select)
        algorithm = algo_select.value

        start, end, description = self.current_graph_info

        algo_name = "Dijkstra's" if algorithm == "dijkstra" else "Bellman-Ford"
        self.update_status(f"Running {algo_name} on {description}...")

        try:
            if algorithm == "dijkstra":
                result = dijkstra(self.current_graph, start)
            else:
                result = bellman_ford(self.current_graph, start)

            display = self.query_one("#graph-display", GraphVisualizer)
            display.set_result(result, start, end, self.seed)

            stats = self.query_one("#stats", StatsDisplay)
            stats.update_stats(result)

            self.update_status(f"{algo_name} finished")

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            import traceback

            traceback.print_exc()

    def action_run(self):
        asyncio.create_task(self.run_algorithm())

    def action_gen(self):
        if self.current_graph and self.current_graph_info and self.current_graph_key:
            self.load_graph(self.current_graph_key)
            self.update_status("Created a new graph. Ready to run algorithm.")

    def action_open_image(self):
        display = self.query_one("#graph-display", GraphVisualizer)
        if display.image_path and os.path.exists(display.image_path):
            import subprocess, platform

            system = platform.system()
            try:
                if system == "Darwin":
                    subprocess.run(["open", display.image_path])
                elif system == "Linux":
                    subprocess.run(["xdg-open", display.image_path])
                elif system == "Windows":
                    os.startfile(display.image_path)
                self.update_status(f"Opened image: {display.image_path}")
            except Exception as e:
                self.update_status(f"Could not open image: {str(e)}")
        else:
            self.update_status("No image to open. Generate a graph first!")

    def get_random_seed(self, min: int = 0, max: int = 99):
        return random.randint(min, max)
