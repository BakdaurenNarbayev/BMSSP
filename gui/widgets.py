from rich.panel import Panel
from textual.widgets import Static
from textual.reactive import reactive


class StatsDisplay(Static):
    """Widget to display algorithm statistics"""

    stats_text = reactive("")

    def render(self):
        return self.stats_text

    def update_stats(self, result=None):
        """Update statistics display"""
        if not result:
            self.stats_text = Panel(
                "Select a graph and algorithm to begin...",
                title="Statistics",
                border_style="blue",
            )
        else:
            content = []
            content.append(f"Algorithm:       {result.algorithm}")
            content.append(f"Execution Time:  {result.execution_time * 1000:.3f} ms")
            # content.append(f"Operations:      {result.operations:,}")
            nodes_reached = sum(
                1 for d in result.distances.values() if d != float("inf")
            )
            content.append(f"Nodes Reached:   {nodes_reached}")

            self.stats_text = Panel(
                "\n".join(content), title="Statistics", border_style="green"
            )
