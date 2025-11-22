"""
Graph Pathfinding Algorithms: Dijkstra and Bellman-Ford
Complete implementation with benchmarking suite
"""

import heapq
import time
import random
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Set
import sys


class Graph:
    """Graph data structure with adjacency list representation"""
    
    def __init__(self, directed: bool = True):
        self.adjacency_list: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        self.directed = directed
        self.node_count = 0
        self.edge_count = 0
    
    # def add_edge(self, from_node: int, to_node: int, weight: float):
    #     """Add an edge to the graph"""
    #     self.adjacency_list[from_node].append((to_node, weight))
    #     if not self.directed:
    #         self.adjacency_list[to_node].append((from_node, weight))
    #         self.edge_count += 1
    #     else:
    #         self.edge_count += 1
        
    #     self.node_count = max(self.node_count, from_node + 1, to_node + 1)

    def add_edge(self, from_node: int, to_node: int, weight: float):
        """
        Add an edge to the graph. If edge already exists, update its weight.
        
        Args:
            from_node: Source node
            to_node: Destination node
            weight: Edge weight
        """
        # Check if edge already exists in from_node's adjacency list
        edge_exists = False
        for i, (node, old_weight) in enumerate(self.adjacency_list[from_node]):
            if node == to_node:
                # Edge exists - update weight
                self.adjacency_list[from_node][i] = (to_node, weight)
                edge_exists = True
                break
        
        # If edge doesn't exist, add it
        if not edge_exists:
            self.adjacency_list[from_node].append((to_node, weight))
            self.edge_count += 1
        
        # Handle undirected graph (add reverse edge)
        if not self.directed:
            # Check if reverse edge exists
            reverse_exists = False
            for i, (node, old_weight) in enumerate(self.adjacency_list[to_node]):
                if node == from_node:
                    # Reverse edge exists - update weight
                    self.adjacency_list[to_node][i] = (from_node, weight)
                    reverse_exists = True
                    break
            
            # If reverse edge doesn't exist, add it
            if not reverse_exists:
                self.adjacency_list[to_node].append((from_node, weight))
                # Don't increment edge_count again for undirected (already counted above)
        
        # Update node count
        self.node_count = max(self.node_count, from_node + 1, to_node + 1)

    
    def get_neighbors(self, node: int) -> List[Tuple[int, float]]:
        """Get all neighbors of a node"""
        return self.adjacency_list.get(node, [])
    
    def get_all_edges(self) -> List[Tuple[int, int, float]]:
        """Get all edges in the graph"""
        edges = []
        seen = set()
        for from_node, neighbors in self.adjacency_list.items():
            for to_node, weight in neighbors:
                if self.directed or (from_node, to_node) not in seen:
                    edges.append((from_node, to_node, weight))
                    if not self.directed:
                        seen.add((to_node, from_node))
        return edges
    
    def __str__(self):
        return f"Graph(nodes={self.node_count}, edges={self.edge_count}, directed={self.directed})"


class PathResult:
    """Result of a pathfinding algorithm"""
    
    def __init__(self, distances: Dict[int, float], previous: Dict[int, Optional[int]], 
                 execution_time: float, operations: int, algorithm: str):
        self.distances = distances
        self.previous = previous
        self.execution_time = execution_time
        self.operations = operations
        self.algorithm = algorithm
    
    def get_path(self, start: int, end: int) -> Optional[List[int]]:
        """Reconstruct path from start to end"""
        if self.distances.get(end, float('inf')) == float('inf'):
            return None
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = self.previous.get(current)
        
        path.reverse()
        return path if path[0] == start else None
    
    def get_distance(self, node: int) -> float:
        """Get distance to a node"""
        return self.distances.get(node, float('inf'))
    
    def __str__(self):
        return (f"{self.algorithm} Result:\n"
                f"  Execution Time: {self.execution_time:.6f} seconds\n"
                f"  Operations: {self.operations:,}\n"
                f"  Nodes Reached: {sum(1 for d in self.distances.values() if d != float('inf'))}")


def dijkstra(graph: Graph, start: int, end: Optional[int] = None) -> PathResult:
    """
    Dijkstra's algorithm for finding shortest paths.
    
    Time Complexity: O((V + E) log V) with binary heap
    Space Complexity: O(V)
    
    Args:
        graph: The graph to search
        start: Starting node
        end: Optional ending node (for early termination)
    
    Returns:
        PathResult containing distances, previous nodes, and metrics
    """
    start_time = time.perf_counter()
    
    # Initialize distances and previous nodes
    distances = {start: 0}
    previous = {start: None}
    visited = set()
    
    # Priority queue: (distance, node)
    pq = [(0, start)]
    operations = 0
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        operations += 1
        
        # Skip if already visited
        if current in visited:
            continue
        
        visited.add(current)
        
        # Early termination if we reached the end
        if end is not None and current == end:
            break
        
        # Explore neighbors
        for neighbor, weight in graph.get_neighbors(current):
            if neighbor not in visited:
                distance = current_dist + weight
                
                # Update if we found a shorter path
                if distance < distances.get(neighbor, float('inf')):
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
                    operations += 1
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return PathResult(distances, previous, execution_time, operations, "Dijkstra")


def bellman_ford(graph: Graph, start: int) -> PathResult:
    """
    Bellman-Ford algorithm for finding shortest paths.
    Can handle negative edge weights and detect negative cycles.
    
    Time Complexity: O(V * E)
    Space Complexity: O(V)
    
    Args:
        graph: The graph to search
        start: Starting node
    
    Returns:
        PathResult containing distances, previous nodes, and metrics
    
    Raises:
        ValueError: If a negative cycle is detected
    """
    start_time = time.perf_counter()
    
    # Initialize distances and previous nodes
    distances = {i: float('inf') for i in range(graph.node_count)}
    distances[start] = 0
    previous = {i: None for i in range(graph.node_count)}
    
    edges = graph.get_all_edges()
    operations = 0
    
    # Relax edges V-1 times
    for _ in range(graph.node_count - 1):
        updated = False
        
        for from_node, to_node, weight in edges:
            operations += 1
            
            # Relax edge if we found a shorter path
            if distances[from_node] != float('inf'):
                new_distance = distances[from_node] + weight
                if new_distance < distances[to_node]:
                    distances[to_node] = new_distance
                    previous[to_node] = from_node
                    updated = True
        
        # Early termination if no updates
        if not updated:
            break
    
    # Check for negative cycles
    for from_node, to_node, weight in edges:
        if distances[from_node] != float('inf'):
            if distances[from_node] + weight < distances[to_node]:
                raise ValueError("Graph contains a negative cycle")
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return PathResult(distances, previous, execution_time, operations, "Bellman-Ford")


def generate_grid_graph(rows: int, cols: int, directed: bool = True) -> Graph:
    """Generate a grid graph with random edge weights"""
    graph = Graph(directed=directed)
    
    for i in range(rows * cols):
        row = i // cols
        col = i % cols
        
        # Connect to right neighbor
        if col < cols - 1:
            weight = random.uniform(1, 10)
            graph.add_edge(i, i + 1, weight)
        
        # Connect to bottom neighbor
        if row < rows - 1:
            weight = random.uniform(1, 10)
            graph.add_edge(i, i + cols, weight)
    
    return graph


def generate_random_graph(num_nodes: int, num_edges: int, directed: bool = True,
                         min_weight: float = 1, max_weight: float = 10) -> Graph:
    """Generate a random graph with specified nodes and edges"""
    graph = Graph(directed=directed)
    
    # Ensure connectivity with a spanning tree first
    for i in range(1, num_nodes):
        parent = random.randint(0, i - 1)
        weight = random.uniform(min_weight, max_weight)
        graph.add_edge(parent, i, weight)
    
    # Add remaining random edges
    edges_added = num_nodes - 1
    attempts = 0
    max_attempts = num_edges * 10
    
    while edges_added < num_edges and attempts < max_attempts:
        from_node = random.randint(0, num_nodes - 1)
        to_node = random.randint(0, num_nodes - 1)
        
        if from_node != to_node:
            # Check if edge already exists
            if not any(n == to_node for n, _ in graph.get_neighbors(from_node)):
                weight = random.uniform(min_weight, max_weight)
                graph.add_edge(from_node, to_node, weight)
                edges_added += 1
        
        attempts += 1
    
    return graph


def generate_complete_graph(num_nodes: int, directed: bool = True) -> Graph:
    """Generate a complete graph where every node is connected to every other node"""
    graph = Graph(directed=directed)
    
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            weight = random.uniform(1, 10)
            graph.add_edge(i, j, weight)
    
    return graph


class Benchmark:
    """Benchmarking suite for pathfinding algorithms"""
    
    def __init__(self):
        self.results = []
    
    def run_benchmark(self, graph: Graph, start: int, end: int, 
                     algorithm: str = "both") -> Dict:
        """
        Run benchmark for specified algorithm(s)
        
        Args:
            graph: Graph to test on
            start: Start node
            end: End node
            algorithm: "dijkstra", "bellman_ford", or "both"
        
        Returns:
            Dictionary with benchmark results
        """
        results = {
            'graph_info': {
                'nodes': graph.node_count,
                'edges': graph.edge_count,
                'directed': graph.directed
            }
        }
        
        if algorithm in ["dijkstra", "both"]:
            print(f"Running Dijkstra's algorithm...")
            dijkstra_result = dijkstra(graph, start, end)
            path = dijkstra_result.get_path(start, end)
            
            results['dijkstra'] = {
                'execution_time': dijkstra_result.execution_time,
                'operations': dijkstra_result.operations,
                'path_length': dijkstra_result.get_distance(end),
                'path_hops': len(path) - 1 if path else None,
                'path': path,
                'nodes_reached': sum(1 for d in dijkstra_result.distances.values() 
                                   if d != float('inf'))
            }
        
        if algorithm in ["bellman_ford", "both"]:
            print(f"Running Bellman-Ford algorithm...")
            try:
                bf_result = bellman_ford(graph, start)
                path = bf_result.get_path(start, end)
                
                results['bellman_ford'] = {
                    'execution_time': bf_result.execution_time,
                    'operations': bf_result.operations,
                    'path_length': bf_result.get_distance(end),
                    'path_hops': len(path) - 1 if path else None,
                    'path': path,
                    'nodes_reached': sum(1 for d in bf_result.distances.values() 
                                       if d != float('inf'))
                }
            except ValueError as e:
                results['bellman_ford'] = {'error': str(e)}
        
        self.results.append(results)
        return results
    
    def print_results(self, results: Dict):
        """Pretty print benchmark results"""
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)
        
        # Graph info
        info = results['graph_info']
        print(f"\nGraph: {info['nodes']:,} nodes, {info['edges']:,} edges "
              f"({'directed' if info['directed'] else 'undirected'})")
        
        # Dijkstra results
        if 'dijkstra' in results:
            print("\n" + "-"*70)
            print("DIJKSTRA'S ALGORITHM")
            print("-"*70)
            d = results['dijkstra']
            print(f"Execution Time:    {d['execution_time']:.6f} seconds")
            print(f"Operations:        {d['operations']:,}")
            print(f"Nodes Reached:     {d['nodes_reached']:,}")
            print(f"Path Length:       {d['path_length']:.2f}" if d['path_length'] != float('inf') 
                  else "Path Length:       No path found")
            print(f"Path Hops:         {d['path_hops']}" if d['path_hops'] is not None 
                  else "Path Hops:         -")
            if d['path'] and len(d['path']) <= 20:
                print(f"Path:              {' -> '.join(map(str, d['path']))}")
        
        # Bellman-Ford results
        if 'bellman_ford' in results:
            print("\n" + "-"*70)
            print("BELLMAN-FORD ALGORITHM")
            print("-"*70)
            bf = results['bellman_ford']
            if 'error' in bf:
                print(f"Error: {bf['error']}")
            else:
                print(f"Execution Time:    {bf['execution_time']:.6f} seconds")
                print(f"Operations:        {bf['operations']:,}")
                print(f"Nodes Reached:     {bf['nodes_reached']:,}")
                print(f"Path Length:       {bf['path_length']:.2f}" if bf['path_length'] != float('inf') 
                      else "Path Length:       No path found")
                print(f"Path Hops:         {bf['path_hops']}" if bf['path_hops'] is not None 
                      else "Path Hops:         -")
                if bf['path'] and len(bf['path']) <= 20:
                    print(f"Path:              {' -> '.join(map(str, bf['path']))}")
        
        # Comparison
        if 'dijkstra' in results and 'bellman_ford' in results and 'error' not in results['bellman_ford']:
            print("\n" + "-"*70)
            print("COMPARISON")
            print("-"*70)
            d = results['dijkstra']
            bf = results['bellman_ford']
            
            speedup = bf['execution_time'] / d['execution_time']
            print(f"Time Ratio (BF/D): {speedup:.2f}x")
            print(f"Dijkstra is {speedup:.2f}x faster" if speedup > 1 
                  else f"Bellman-Ford is {1/speedup:.2f}x faster")
            
            op_ratio = bf['operations'] / max(d['operations'], 1)
            print(f"\nOperation Ratio:   {op_ratio:.2f}x")
            print(f"Dijkstra: {d['operations']:,} operations")
            print(f"Bellman-Ford: {bf['operations']:,} operations")
            
            # Verify same path length
            if abs(d['path_length'] - bf['path_length']) < 0.001:
                print(f"\n✓ Both algorithms found the same shortest path length: {d['path_length']:.2f}")
            else:
                print(f"\n✗ WARNING: Different path lengths found!")
                print(f"  Dijkstra: {d['path_length']:.2f}")
                print(f"  Bellman-Ford: {bf['path_length']:.2f}")
        
        print("\n" + "="*70 + "\n")
    
    def run_scalability_test(self):
        """Run benchmarks with increasing graph sizes"""
        print("\n" + "="*70)
        print("SCALABILITY TEST")
        print("="*70 + "\n")
        
        test_sizes = [
            (10, 20),      # Small
            (50, 100),     # Medium
            (100, 300),    # Large
            (500, 1500),   # Very Large
        ]
        
        for nodes, edges in test_sizes:
            print(f"\nTesting with {nodes} nodes, {edges} edges...")
            graph = generate_random_graph(nodes, edges)
            start = 0
            end = nodes - 1
            
            results = self.run_benchmark(graph, start, end, algorithm="both")
            
            # Print summary
            if 'dijkstra' in results and 'bellman_ford' in results:
                d_time = results['dijkstra']['execution_time']
                bf_time = results['bellman_ford']['execution_time']
                print(f"  Dijkstra:     {d_time:.6f}s")
                print(f"  Bellman-Ford: {bf_time:.6f}s")
                print(f"  Speedup:      {bf_time/d_time:.2f}x")


def demo():
    """Demonstration of the algorithms"""
    print("\n" + "="*70)
    print("DIJKSTRA & BELLMAN-FORD ALGORITHM DEMONSTRATION")
    print("="*70 + "\n")
    
    # Create a simple test graph
    print("Creating a simple weighted graph...")
    graph = Graph(directed=False)
    
    # Example graph from common algorithm tutorials
    edges = [
        (0, 1, 4),
        (0, 2, 1),
        (1, 3, 1),
        (2, 1, 2),
        (2, 3, 5),
        (3, 4, 3),
    ]
    
    for from_node, to_node, weight in edges:
        graph.add_edge(from_node, to_node, weight)
    
    print(f"Created graph with {graph.node_count} nodes and {graph.edge_count} edges")
    print("\nEdges:")
    for from_node, to_node, weight in edges:
        print(f"  {from_node} --[{weight}]--> {to_node}")
    
    # Run benchmarks
    benchmark = Benchmark()
    start, end = 0, 4
    print(f"\nFinding shortest path from node {start} to node {end}...")
    
    results = benchmark.run_benchmark(graph, start, end, algorithm="both")
    benchmark.print_results(results)
    
    # Run scalability test
    response = input("Run scalability test? (y/n): ")
    if response.lower() == 'y':
        benchmark.run_scalability_test()


def main():
    """Main function with various benchmark scenarios"""
    print("\nGraph Pathfinding Algorithm Benchmarking Suite")
    print("=" * 70)
    print("\nOptions:")
    print("1. Run demonstration with simple graph")
    print("2. Benchmark on grid graph")
    print("3. Benchmark on random graph")
    print("4. Benchmark on complete graph")
    print("5. Run scalability test")
    print("6. Custom benchmark")
    
    try:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        benchmark = Benchmark()
        
        if choice == '1':
            demo()
        
        elif choice == '2':
            rows = int(input("Enter number of rows: "))
            cols = int(input("Enter number of columns: "))
            print(f"\nGenerating {rows}x{cols} grid graph...")
            graph = generate_grid_graph(rows, cols)
            start = 0
            end = rows * cols - 1
            results = benchmark.run_benchmark(graph, start, end, algorithm="both")
            benchmark.print_results(results)
        
        elif choice == '3':
            nodes = int(input("Enter number of nodes: "))
            edges = int(input("Enter number of edges: "))
            print(f"\nGenerating random graph with {nodes} nodes and {edges} edges...")
            graph = generate_random_graph(nodes, edges)
            start = 0
            end = nodes - 1
            results = benchmark.run_benchmark(graph, start, end, algorithm="both")
            benchmark.print_results(results)
        
        elif choice == '4':
            nodes = int(input("Enter number of nodes: "))
            print(f"\nGenerating complete graph with {nodes} nodes...")
            graph = generate_complete_graph(nodes)
            start = 0
            end = nodes - 1
            results = benchmark.run_benchmark(graph, start, end, algorithm="both")
            benchmark.print_results(results)
        
        elif choice == '5':
            benchmark.run_scalability_test()
        
        elif choice == '6':
            nodes = int(input("Enter number of nodes: "))
            edges = int(input("Enter number of edges: "))
            start = int(input("Enter start node: "))
            end = int(input("Enter end node: "))
            algo = input("Algorithm (dijkstra/bellman_ford/both): ").strip().lower()
            
            print(f"\nGenerating graph...")
            graph = generate_random_graph(nodes, edges)
            results = benchmark.run_benchmark(graph, start, end, algorithm=algo)
            benchmark.print_results(results)
        
        else:
            print("Invalid choice!")
    
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
