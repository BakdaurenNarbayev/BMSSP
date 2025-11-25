import os
import re
import random
import shutil
import asyncio
import platform
import subprocess
from pathlib import Path
from widgets import StatsDisplay
from visualizer import GraphVisualizer
from benchmark.main import run_benchmark
from textual.app import App, ComposeResult
from graph_algorithms import dijkstra, bellman_ford
from sample_graphs import GRAPH_SIZES, create_sample_graphs
from textual.widgets import Header, Footer, Button, Select, Label, Static
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer


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
    #benchmark-controls {
        height: auto;
        background: $panel-darken-1;
        padding: 1 2;
        border-top: solid $primary;
        border-bottom: solid $primary;
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
    .benchmark-label { 
        padding: 0 1; 
        color: $accent; 
        text-style: bold;
    }
    GraphVisualizer { height: 100%; overflow-y: auto; }
    #info-panel { padding: 1 2; background: $surface; height: auto; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "run", "Run Algorithm"),
        ("g", "gen", "Generate New Graph"),
        ("o", "open_image", "Open Image"),
        ("b", "run_benchmark", "Run Benchmark"),
    ]

    def __init__(self):
        super().__init__()
        self.graphs = list(GRAPH_SIZES.keys())
        self.current_graph = None
        self.current_graph_key = None
        self.current_graph_info = None
        self.current_algorithm = None
        self.seed = self.get_random_seed()
        self.benchmark_completed = False
        self.results_file_path = None
        self.required_force_save = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Main algorithm controls
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

        # Benchmark controls section
        with Container(id="benchmark-controls"):
            with Horizontal(classes="control-row"):
                yield Label("BENCHMARK", classes="benchmark-label")
            with Horizontal(classes="control-row"):
                yield Button("Run Benchmark", variant="success", id="benchmark-run-btn")
                yield Button(
                    "Open Config", variant="default", id="benchmark-config-btn"
                )
                yield Button(
                    "Open Results",
                    variant="default",
                    id="benchmark-results-btn",
                    disabled=True,
                )

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

    def on_unmount(self):
        """Called when the app is shutting down"""
        self.delete_result_folder()

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
        elif event.button.id == "benchmark-run-btn":
            await self.run_benchmark()
        elif event.button.id == "benchmark-config-btn":
            self.open_config_file()
        elif event.button.id == "benchmark-results-btn":
            self.open_results_plot()

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

    async def run_benchmark(self):
        """Run the benchmark suite"""
        self.update_status("Starting benchmark...")

        try:
            self.delete_result_folder()
            (_, plot_file), required_force_save = run_benchmark(force_save=True)
            self.results_file_path = plot_file
            self.required_force_save = required_force_save

            self.benchmark_completed = True
            results_btn = self.query_one("#benchmark-results-btn", Button)
            results_btn.disabled = False

            self.update_status("Benchmark completed successfully!")
        except Exception as e:
            self.update_status(f"Benchmark error: {str(e)}")

    def open_config_file(self):
        """Open the benchmark configuration file"""
        config_file = "config/main.yaml"

        if os.path.exists(config_file):
            import subprocess, platform

            system = platform.system()
            try:
                if system == "Darwin":
                    subprocess.run(["open", config_file])
                elif system == "Linux":
                    subprocess.run(["xdg-open", config_file])
                elif system == "Windows":
                    os.startfile(config_file)
                self.update_status(f"Opened config: {config_file}")
            except Exception as e:
                self.update_status(f"Could not open config: {str(e)}")
        else:
            self.update_status(f"Config file not found: {config_file}")

    def open_results_plot(self):
        """Open the benchmark results PDF plot"""
        if not self.benchmark_completed:
            self.update_status("Please run benchmark first or wait for it to complete!")
            return

        if self.results_file_path and os.path.exists(self.results_file_path):
            system = platform.system()
            try:
                if system == "Darwin":
                    subprocess.run(["open", self.results_file_path])
                elif system == "Linux":
                    subprocess.run(["xdg-open", self.results_file_path])
                elif system == "Windows":
                    os.startfile(self.results_file_path)
                self.update_status(f"Opened results plot: {self.results_file_path}")
            except Exception as e:
                self.update_status(f"Could not open results plot: {str(e)}")
        else:
            self.update_status(
                f"Results plot not found. Expected PDF in: {self.results_file_path}"
            )

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

    def action_run_benchmark(self):
        asyncio.create_task(self.run_benchmark())

    def get_random_seed(self, min: int = 0, max: int = 99):
        return random.randint(min, max)

    def delete_result_folder(self):
        if self.results_file_path is None or not self.required_force_save:
            return

        try:
            results_path = Path(self.results_file_path)
            results_folder = results_path.parent

            if results_folder.exists() and results_folder.is_dir():
                shutil.rmtree(results_folder)

            self.results_file_path = None
            self.benchmark_completed = False
            self.required_force_save = False

            results_btn = self.query_one("#benchmark-results-btn", Button)
            results_btn.disabled = True
        except Exception as e:
            self.notify(f"Failed to delete temporary results: {str(e)}")
