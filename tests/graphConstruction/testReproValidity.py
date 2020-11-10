import unittest
from networkx import*
from GraphConstruction.SNAMeasures import Monoplex

class TestSNAMeasures(unittest.TestCase):

    def test_reachabilitySCC(self):
        # Create directed graph with edges from E
        E = [(0, 1), (1, 2), (1, 0), (2, 3), (3, 0)]
        reachability = {0: 4, 1: 4, 2: 4, 3: 4}
        G = networkx.DiGraph()
        for e in E:
            G.add_edge(e[0], e[1])
        graph = Monoplex(G, True, None)

        self.assertEqual(graph.computeReachability(), reachability)

    def test_reachabilityMultipleSCC(self):
        # Create directed graph with edges from E
        E = [(0, 1), (1, 2), (1, 0), (2, 3)]
        reachability = {0: 4, 1: 4, 2: 1, 3: 0}
        G = networkx.DiGraph()
        for e in E:
            G.add_edge(e[0], e[1])
        graph = Monoplex(G, True, None)

        self.assertEqual(graph.computeReachability(), reachability)

if __name__ == '__main__':
    unittest.main()
