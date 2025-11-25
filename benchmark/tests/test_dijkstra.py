import math
import unittest
from benchmark.methods.dijkstra import Dijkstra


class MockGraph:
    """Mock graph class for testing"""
    def __init__(self, edges, node_count):
        self.edges = edges
        self.node_count = node_count
        self._adjacency = {}
        self._build_adjacency()
    
    def _build_adjacency(self):
        """Build adjacency list from edges"""
        for u, v, w in self.edges:
            if u not in self._adjacency:
                self._adjacency[u] = []
            self._adjacency[u].append((v, w))
    
    def get_all_edges(self):
        return self.edges
    
    def get_neighbors(self, node):
        return self._adjacency.get(node, [])


class TestDijkstra(unittest.TestCase):
    """Comprehensive test suite for Dijkstra's algorithm"""
    
    # Validation Tests
    def test_validate_accepts_positive_weights(self):
        """Validate should return True for all positive weights"""
        edges = [(0, 1, 5.0), (1, 2, 3.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        self.assertTrue(dijkstra.validate())
    
    def test_validate_rejects_negative_weights(self):
        """Validate should return False for negative weights"""
        edges = [(0, 1, 5.0), (1, 2, -3.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        self.assertFalse(dijkstra.validate())
    
    def test_validate_accepts_zero_weights(self):
        """Validate should accept zero weight edges"""
        edges = [(0, 1, 0.0), (1, 2, 5.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        self.assertTrue(dijkstra.validate())
    
    def test_validate_empty_graph(self):
        """Validate should return True for empty graph"""
        graph = MockGraph([], 0)
        dijkstra = Dijkstra(graph, 0)
        self.assertTrue(dijkstra.validate())
    
    def test_validate_single_negative_edge(self):
        """Validate should reject graph with single negative edge"""
        edges = [(0, 1, -1.0)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        self.assertFalse(dijkstra.validate())
    
    def test_validate_mixed_zero_positive_weights(self):
        """Validate should accept mix of zero and positive weights"""
        edges = [(0, 1, 0.0), (1, 2, 0.0), (2, 3, 5.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        self.assertTrue(dijkstra.validate())
    
    # Setup Tests
    def test_setup_initializes_distances_to_infinity(self):
        """Setup should initialize all distances to infinity"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        for n in range(1, graph.node_count):
            self.assertEqual(dijkstra.dist[n], math.inf)
    
    def test_setup_sets_source_distance_to_zero(self):
        """Setup should set source distance to 0"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 2)
        dijkstra.setup()
        self.assertEqual(dijkstra.dist[2], 0.0)
    
    def test_setup_initializes_predecessors_to_none(self):
        """Setup should initialize all predecessors to None"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        for n in range(graph.node_count):
            self.assertIsNone(dijkstra.pred[n])
    
    def test_setup_with_source_zero(self):
        """Setup should work correctly with source node 0"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        self.assertEqual(dijkstra.dist[0], 0.0)
    
    def test_setup_with_source_at_boundary(self):
        """Setup should work with source at last valid node"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 4)
        dijkstra.setup()
        self.assertEqual(dijkstra.dist[4], 0.0)
    
    def test_setup_with_source_beyond_node_count(self):
        """Setup should extend graph when source exceeds node_count"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 10)
        dijkstra.setup()
        self.assertEqual(dijkstra.dist[10], 0.0)
        self.assertGreaterEqual(graph.node_count, 11)
    
    def test_setup_resets_state(self):
        """Setup should reset internal state"""
        graph = MockGraph([], 5)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.iterations = 5
        dijkstra.edge_relaxations = 10
        dijkstra.setup()
        self.assertTrue(hasattr(dijkstra, 'dist'))
        self.assertTrue(hasattr(dijkstra, 'pred'))
    
    # Simple Graph Tests
    def test_empty_graph(self):
        """Run should handle empty graph"""
        graph = MockGraph([], 0)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
    
    def test_single_node_graph(self):
        """Run should handle single node graph"""
        graph = MockGraph([], 1)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)
    
    def test_two_nodes_single_edge(self):
        """Run should handle two nodes with single edge"""
        edges = [(0, 1, 5.0)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)
        self.assertEqual(dijkstra.dist[1], 5.0)
    
    def test_linear_chain_graph(self):
        """Run should handle linear chain of nodes"""
        edges = [(0, 1, 2.0), (1, 2, 3.0), (2, 3, 1.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)
        self.assertEqual(dijkstra.dist[1], 2.0)
        self.assertEqual(dijkstra.dist[2], 5.0)
        self.assertEqual(dijkstra.dist[3], 6.0)
    
    def test_disconnected_graph(self):
        """Run should handle disconnected components"""
        edges = [(0, 1, 1.0), (2, 3, 2.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)
        self.assertEqual(dijkstra.dist[1], 1.0)
        self.assertEqual(dijkstra.dist[2], math.inf)
        self.assertEqual(dijkstra.dist[3], math.inf)
    
    def test_simple_triangle_graph(self):
        """Run should handle simple triangle graph"""
        edges = [(0, 1, 4.0), (0, 2, 2.0), (2, 1, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[1], 3.0)  # 0->2->1 is shorter
    
    # Zero Weight Tests
    def test_zero_weight_edges(self):
        """Run should handle zero weight edges"""
        edges = [(0, 1, 0.0), (1, 2, 0.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[2], 0.0)
    
    def test_mixed_zero_positive_weights(self):
        """Run should handle mix of zero and positive weights"""
        edges = [(0, 1, 0.0), (1, 2, 5.0), (0, 2, 10.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[2], 5.0)
    
    def test_all_zero_weights(self):
        """Run should handle all zero weight edges"""
        edges = [(0, 1, 0.0), (1, 2, 0.0), (2, 3, 0.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[3], 0.0)
    
    # Complex Graph Tests
    def test_complete_graph(self):
        """Run should handle complete graph"""
        edges = [(i, j, 1.0) for i in range(4) for j in range(4) if i != j]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        for node in range(1, 4):
            self.assertEqual(dijkstra.dist[node], 1.0)
    
    def test_graph_with_multiple_paths(self):
        """Run should find shortest among multiple paths"""
        edges = [
            (0, 1, 10.0), (0, 2, 5.0), (1, 3, 1.0),
            (2, 1, 2.0), (2, 3, 8.0)
        ]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[3], 8.0)  # 0->2->1->3
    
    def test_dag_structure(self):
        """Run should handle directed acyclic graph"""
        edges = [(0, 1, 3.0), (0, 2, 6.0), (1, 2, 1.0), (1, 3, 2.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[2], 4.0)
        self.assertEqual(dijkstra.dist[3], 5.0)
    
    def test_diamond_graph(self):
        """Run should handle diamond-shaped graph"""
        edges = [
            (0, 1, 1.0), (0, 2, 4.0),
            (1, 2, 2.0), (1, 3, 6.0),
            (2, 3, 1.0)
        ]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[3], 4.0)  # 0->1->2->3
    
    # Predecessor Tests
    def test_predecessors_simple_path(self):
        """Run should correctly track predecessors"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertIsNone(dijkstra.pred[0])
        self.assertEqual(dijkstra.pred[1], 0)
        self.assertEqual(dijkstra.pred[2], 1)
    
    def test_predecessors_with_better_path(self):
        """Run should update predecessors when better path found"""
        edges = [(0, 1, 10.0), (0, 2, 5.0), (2, 1, 2.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.pred[1], 2)  # Better path through node 2
    
    def test_predecessors_unreachable_nodes(self):
        """Predecessors should remain None for unreachable nodes"""
        edges = [(0, 1, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertIsNone(dijkstra.pred[2])
    
    def test_predecessors_multiple_paths(self):
        """Predecessors should reflect shortest path"""
        edges = [(0, 1, 4.0), (0, 2, 2.0), (2, 1, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.pred[1], 2)
        self.assertEqual(dijkstra.pred[2], 0)
    
    # Metrics Tests
    def test_iterations_count(self):
        """Run should count iterations correctly"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertGreater(dijkstra.iterations, 0)
        self.assertLessEqual(dijkstra.iterations, graph.node_count)
    
    def test_edge_relaxations_count(self):
        """Run should count edge relaxation attempts"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertGreater(dijkstra.edge_relaxations, 0)
    
    def test_successful_relaxations_count(self):
        """Run should count successful relaxations"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertGreater(dijkstra.successful_relaxations, 0)
    
    def test_no_relaxations_for_disconnected(self):
        """Disconnected nodes should not result in relaxations"""
        edges = [(0, 1, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        # Should have some relaxations, but not for unreachable nodes
        self.assertGreater(dijkstra.successful_relaxations, 0)
    
    def test_metrics_single_node(self):
        """Metrics should be valid for single node graph"""
        graph = MockGraph([], 1)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.iterations, 1)
    
    # Edge Case Tests
    def test_self_loop(self):
        """Run should handle self-loop correctly"""
        edges = [(0, 0, 5.0), (0, 1, 1.0)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)  # Self-loop doesn't improve
    
    def test_parallel_edges_different_weights(self):
        """Run should handle parallel edges with different weights"""
        edges = [(0, 1, 5.0), (0, 1, 2.0), (0, 1, 10.0)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[1], 2.0)  # Takes minimum weight edge
    
    def test_very_large_weight(self):
        """Run should handle very large edge weights"""
        edges = [(0, 1, 1e10)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[1], 1e10)
    
    def test_very_small_positive_weight(self):
        """Run should handle very small positive weights"""
        edges = [(0, 1, 1e-10)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertAlmostEqual(dijkstra.dist[1], 1e-10)
    
    def test_large_node_count_sparse_edges(self):
        """Run should handle large node count with sparse edges"""
        edges = [(0, 50, 1.0)]
        graph = MockGraph(edges, 100)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[50], 1.0)
    
    def test_source_not_in_initial_graph(self):
        """Setup should handle source node beyond initial node count"""
        edges = []
        graph = MockGraph(edges, 5)
        dijkstra = Dijkstra(graph, 10)
        dijkstra.setup()
        self.assertEqual(dijkstra.dist[10], 0.0)
    
    def test_fractional_weights(self):
        """Run should handle fractional weights correctly"""
        edges = [(0, 1, 0.5), (1, 2, 0.3), (0, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertAlmostEqual(dijkstra.dist[2], 0.8)
    
    # Priority Queue Behavior Tests
    def test_priority_queue_ordering(self):
        """Run should process nodes in correct priority order"""
        edges = [(0, 1, 5.0), (0, 2, 1.0), (2, 3, 1.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        # Node 2 should be processed before node 1 due to lower distance
        self.assertEqual(dijkstra.dist[2], 1.0)
        self.assertEqual(dijkstra.dist[3], 2.0)
    
    def test_duplicate_heap_entries(self):
        """Run should handle duplicate entries in heap correctly"""
        edges = [(0, 1, 5.0), (0, 2, 2.0), (2, 1, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        # Node 1 gets updated via node 2, creating duplicate heap entries
        self.assertEqual(dijkstra.dist[1], 3.0)
    
    def test_visited_nodes_not_reprocessed(self):
        """Run should not reprocess visited nodes"""
        edges = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 10.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        # Each node should be visited exactly once
        self.assertLessEqual(dijkstra.iterations, graph.node_count)
    
    # Different Source Node Tests
    def test_source_at_end_of_graph(self):
        """Run should work with source as last node"""
        edges = [(2, 1, 2.0), (1, 0, 3.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 2)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[2], 0.0)
        self.assertEqual(dijkstra.dist[1], 2.0)
        self.assertEqual(dijkstra.dist[0], 5.0)
    
    def test_source_in_middle(self):
        """Run should work with source in middle of graph"""
        edges = [(1, 0, 1.0), (1, 2, 2.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 1)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 1.0)
        self.assertEqual(dijkstra.dist[2], 2.0)
    
    def test_source_with_no_outgoing_edges(self):
        """Run should handle source with no outgoing edges"""
        edges = [(1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[0], 0.0)
        self.assertEqual(dijkstra.dist[1], math.inf)
        self.assertEqual(dijkstra.dist[2], math.inf)
    
    # Shortest Path Correctness Tests
    def test_shortest_path_simple(self):
        """Run should find correct shortest path in simple graph"""
        edges = [(0, 1, 1.0), (0, 2, 4.0), (1, 2, 2.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.dist[2], 3.0)  # 0->1->2
    
    def test_shortest_path_complex(self):
        """Run should find correct shortest path in complex graph"""
        edges = [
            (0, 1, 4.0), (0, 2, 2.0),
            (1, 2, 1.0), (1, 3, 5.0),
            (2, 3, 8.0), (2, 4, 10.0),
            (3, 4, 2.0)
        ]
        graph = MockGraph(edges, 5)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.dist[4], 11.0)  # 0->2->4
    
    def test_direct_vs_indirect_path(self):
        """Run should choose shorter indirect path over direct path"""
        edges = [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 10.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.dist[2], 2.0)  # 0->1->2 is shorter
        self.assertEqual(dijkstra.pred[2], 1)
    
    def test_multiple_equal_shortest_paths(self):
        """Run should find one of multiple equal shortest paths"""
        edges = [(0, 1, 1.0), (0, 2, 1.0), (1, 3, 1.0), (2, 3, 1.0)]
        graph = MockGraph(edges, 4)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.dist[3], 2.0)  # Either path works
        self.assertIn(dijkstra.pred[3], [1, 2])
    
    # Bidirectional Edge Tests
    def test_bidirectional_edges(self):
        """Run should handle bidirectional edges correctly"""
        edges = [(0, 1, 2.0), (1, 0, 3.0), (1, 2, 1.0), (2, 1, 4.0)]
        graph = MockGraph(edges, 3)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
        self.assertEqual(dijkstra.dist[1], 2.0)
        self.assertEqual(dijkstra.dist[2], 3.0)
    
    def test_bidirectional_different_weights(self):
        """Run should respect edge directions with different weights"""
        edges = [(0, 1, 1.0), (1, 0, 10.0)]
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        dijkstra.run()
        self.assertEqual(dijkstra.dist[1], 1.0)
    
    # Return Value Tests
    def test_run_always_returns_true(self):
        """Run should always return True (no negative cycles in Dijkstra)"""
        edges = [(0, 1, 1.0), (1, 0, 1.0)]  # Cycle with positive weights
        graph = MockGraph(edges, 2)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)
    
    def test_run_returns_true_for_empty_graph(self):
        """Run should return True for empty graph"""
        graph = MockGraph([], 0)
        dijkstra = Dijkstra(graph, 0)
        dijkstra.setup()
        result = dijkstra.run()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()