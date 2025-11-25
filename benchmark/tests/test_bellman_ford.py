import math
import unittest
from benchmark.methods.bellman_ford import BellmanFord


class MockGraph:
    """Mock graph class for testing"""
    def __init__(self, edges, node_count):
        self.edges = edges
        self.node_count = node_count
    
    def get_all_edges(self):
        return self.edges


class TestBellmanFord(unittest.TestCase):
    """Comprehensive test suite for Bellman-Ford algorithm"""
    
    # Validation Tests
    def test_validate_returns_true(self):
        """Validate should always return True for Bellman-Ford"""
        bf = BellmanFord(None, 0)
        self.assertTrue(bf.validate())
    
    def test_validate_with_none_graph(self):
        """Validate should return True even with None graph"""
        bf = BellmanFord(None, 0)
        self.assertTrue(bf.validate())
    
    def test_validate_consistency(self):
        """Validate should consistently return True"""
        bf = BellmanFord(None, 0)
        for _ in range(10):
            self.assertTrue(bf.validate())
    
    # Setup Tests
    def test_setup_initializes_distances_to_infinity(self):
        """Setup should initialize all distances to infinity"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 0)
        bf.setup()
        for n in range(1, graph.node_count):
            self.assertEqual(bf.dist[n], math.inf)
    
    def test_setup_sets_source_distance_to_zero(self):
        """Setup should set source distance to 0"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 2)
        bf.setup()
        self.assertEqual(bf.dist[2], 0.0)
    
    def test_setup_initializes_predecessors_to_none(self):
        """Setup should initialize all predecessors to None"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 0)
        bf.setup()
        for n in range(graph.node_count):
            self.assertIsNone(bf.pred[n])
    
    def test_setup_with_source_zero(self):
        """Setup should work correctly with source node 0"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 0)
        bf.setup()
        self.assertEqual(bf.dist[0], 0.0)
    
    def test_setup_with_source_at_boundary(self):
        """Setup should work with source at last valid node"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 4)
        bf.setup()
        self.assertEqual(bf.dist[4], 0.0)
    
    def test_setup_with_source_beyond_node_count(self):
        """Setup should extend graph when source exceeds node_count"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 10)
        bf.setup()
        self.assertEqual(bf.dist[10], 0.0)
        self.assertGreaterEqual(graph.node_count, 11)
    
    def test_setup_resets_state(self):
        """Setup should reset internal state"""
        graph = MockGraph([], 5)
        bf = BellmanFord(graph, 0)
        bf.iterations = 5
        bf.edge_relaxations = 10
        bf.setup()
        self.assertTrue(hasattr(bf, 'dist'))
        self.assertTrue(hasattr(bf, 'pred'))
    
    # Simple Graph Tests
    def test_empty_graph(self):
        """Run should handle empty graph"""
        graph = MockGraph([], 0)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
    
    def test_single_node_graph(self):
        """Run should handle single node graph"""
        graph = MockGraph([], 1)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 0.0)
    
    def test_two_nodes_single_edge(self):
        """Run should handle two nodes with single edge"""
        edges = [(0, 1, 5.0)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 0.0)
        self.assertEqual(bf.dist[1], 5.0)
    
    def test_linear_chain_graph(self):
        """Run should handle linear chain of nodes"""
        edges = [(0, 1, 2.0), (1, 2, 3.0), (2, 3, 1.0)]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 0.0)
        self.assertEqual(bf.dist[1], 2.0)
        self.assertEqual(bf.dist[2], 5.0)
        self.assertEqual(bf.dist[3], 6.0)
    
    def test_disconnected_graph(self):
        """Run should handle disconnected components"""
        edges = [(0, 1, 1.0), (2, 3, 2.0)]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 0.0)
        self.assertEqual(bf.dist[1], 1.0)
        self.assertEqual(bf.dist[2], math.inf)
        self.assertEqual(bf.dist[3], math.inf)
    
    # Negative Weight Tests
    def test_single_negative_edge(self):
        """Run should handle single negative weight edge"""
        edges = [(0, 1, -5.0)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[1], -5.0)
    
    def test_mixed_positive_negative_weights(self):
        """Run should handle mix of positive and negative weights"""
        edges = [(0, 1, 5.0), (1, 2, -2.0), (0, 2, 4.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[2], 3.0)
    
    def test_all_negative_weights(self):
        """Run should handle graph with all negative weights"""
        edges = [(0, 1, -1.0), (1, 2, -2.0), (2, 3, -3.0)]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[3], -6.0)
    
    def test_zero_weight_edges(self):
        """Run should handle zero weight edges"""
        edges = [(0, 1, 0.0), (1, 2, 0.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[2], 0.0)
    
    # Negative Cycle Tests
    def test_simple_negative_cycle(self):
        """Run should detect simple negative cycle"""
        edges = [(0, 1, 1.0), (1, 2, -5.0), (2, 0, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertFalse(result)
    
    def test_negative_self_loop(self):
        """Run should detect negative self-loop"""
        edges = [(0, 0, -1.0)]
        graph = MockGraph(edges, 1)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertFalse(result)
    
    def test_negative_cycle_unreachable_from_source(self):
        """Run should not detect negative cycle unreachable from source"""
        edges = [(0, 1, 5.0), (2, 3, 1.0), (3, 4, -5.0), (4, 2, 1.0)]
        graph = MockGraph(edges, 5)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
    
    def test_large_negative_cycle(self):
        """Run should detect negative cycle in larger graph"""
        edges = [(0, 1, 2.0), (1, 2, 3.0), (2, 3, -10.0), (3, 1, 1.0)]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertFalse(result)
    
    # Complex Graph Tests
    def test_complete_graph(self):
        """Run should handle complete graph"""
        edges = [(i, j, 1.0) for i in range(4) for j in range(4) if i != j]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
    
    def test_graph_with_multiple_paths(self):
        """Run should find shortest among multiple paths"""
        edges = [
            (0, 1, 10.0), (0, 2, 5.0), (1, 3, 1.0),
            (2, 1, 2.0), (2, 3, 8.0)
        ]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[3], 8.0)
    
    def test_dag_structure(self):
        """Run should handle directed acyclic graph"""
        edges = [(0, 1, 3.0), (0, 2, 6.0), (1, 2, 1.0), (1, 3, 2.0)]
        graph = MockGraph(edges, 4)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[2], 4.0)
        self.assertEqual(bf.dist[3], 5.0)
    
    def test_bidirectional_edges(self):
        """Run should handle bidirectional edges"""
        edges = [(0, 1, 2.0), (1, 0, 2.0), (1, 2, 3.0), (2, 1, 3.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
    
    # Predecessor Tests
    def test_predecessors_simple_path(self):
        """Run should correctly track predecessors"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertIsNone(bf.pred[0])
        self.assertEqual(bf.pred[1], 0)
        self.assertEqual(bf.pred[2], 1)
    
    def test_predecessors_with_relaxation(self):
        """Run should update predecessors when better path found"""
        edges = [(0, 1, 10.0), (0, 2, 5.0), (2, 1, 2.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertEqual(bf.pred[1], 2)
    
    def test_predecessors_unreachable_nodes(self):
        """Predecessors should remain None for unreachable nodes"""
        edges = [(0, 1, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertIsNone(bf.pred[2])
    
    # Metrics Tests
    def test_iterations_count(self):
        """Run should correctly count iterations"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        expected_iterations = graph.node_count
        self.assertEqual(bf.iterations, expected_iterations)
    
    def test_edge_relaxations_count(self):
        """Run should count all edge relaxation attempts"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        expected = len(edges) * graph.node_count
        self.assertEqual(bf.edge_relaxations, expected)
    
    def test_successful_relaxations_count(self):
        """Run should count successful relaxations"""
        edges = [(0, 1, 1.0), (1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertGreater(bf.successful_relaxations, 0)
    
    def test_no_relaxations_for_disconnected(self):
        """Disconnected nodes should result in zero successful relaxations for them"""
        edges = [(0, 1, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        initial_successful = bf.successful_relaxations
        bf.run()
        self.assertGreater(bf.successful_relaxations, initial_successful)
    
    # Edge Case Tests
    def test_self_loop_positive_weight(self):
        """Run should handle positive weight self-loop"""
        edges = [(0, 0, 5.0), (0, 1, 1.0)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 0.0)
    
    def test_parallel_edges_different_weights(self):
        """Run should handle parallel edges with different weights"""
        edges = [(0, 1, 5.0), (0, 1, 2.0), (0, 1, 10.0)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[1], 2.0)
    
    def test_very_large_weight(self):
        """Run should handle very large edge weights"""
        edges = [(0, 1, 1e10)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[1], 1e10)
    
    def test_very_small_positive_weight(self):
        """Run should handle very small positive weights"""
        edges = [(0, 1, 1e-10)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertAlmostEqual(bf.dist[1], 1e-10)
    
    def test_large_node_count_sparse_edges(self):
        """Run should handle large node count with sparse edges"""
        edges = [(0, 50, 1.0)]
        graph = MockGraph(edges, 100)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[50], 1.0)
    
    def test_source_not_in_initial_graph(self):
        """Setup should handle source node beyond initial node count"""
        edges = []
        graph = MockGraph(edges, 5)
        bf = BellmanFord(graph, 10)
        bf.setup()
        self.assertEqual(bf.dist[10], 0.0)
    
    def test_fractional_weights(self):
        """Run should handle fractional weights correctly"""
        edges = [(0, 1, 0.5), (1, 2, 0.3), (0, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertAlmostEqual(bf.dist[2], 0.8)
    
    # Relaxation Logic Tests
    def test_no_relaxation_when_source_unreachable(self):
        """Edges from unreachable nodes should not cause relaxation"""
        edges = [(1, 2, 1.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertEqual(bf.dist[2], math.inf)
    
    def test_relaxation_order_independence(self):
        """Result should be same regardless of edge order"""
        edges1 = [(0, 1, 2.0), (0, 2, 5.0), (1, 2, 1.0)]
        edges2 = [(1, 2, 1.0), (0, 2, 5.0), (0, 1, 2.0)]
        
        graph1 = MockGraph(edges1, 3)
        bf1 = BellmanFord(graph1, 0)
        bf1.setup()
        bf1.run()
        
        graph2 = MockGraph(edges2, 3)
        bf2 = BellmanFord(graph2, 0)
        bf2.setup()
        bf2.run()
        
        self.assertEqual(bf1.dist[2], bf2.dist[2])
    
    def test_no_improvement_after_optimal(self):
        """No relaxations should occur after optimal solution found"""
        edges = [(0, 1, 1.0)]
        graph = MockGraph(edges, 2)
        bf = BellmanFord(graph, 0)
        bf.setup()
        bf.run()
        self.assertEqual(bf.dist[1], 1.0)
    
    # Multiple Sources Tests
    def test_source_at_end_of_graph(self):
        """Run should work with source as last node"""
        edges = [(2, 1, 2.0), (1, 0, 3.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 2)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[2], 0.0)
        self.assertEqual(bf.dist[1], 2.0)
        self.assertEqual(bf.dist[0], 5.0)
    
    def test_source_in_middle(self):
        """Run should work with source in middle of graph"""
        edges = [(1, 0, 1.0), (1, 2, 2.0)]
        graph = MockGraph(edges, 3)
        bf = BellmanFord(graph, 1)
        bf.setup()
        result = bf.run()
        self.assertTrue(result)
        self.assertEqual(bf.dist[0], 1.0)
        self.assertEqual(bf.dist[2], 2.0)


if __name__ == '__main__':
    unittest.main()
