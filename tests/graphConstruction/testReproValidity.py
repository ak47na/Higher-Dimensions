import math
import unittest
from networkx import*
from GraphConstruction.SNAMeasures import Monoplex
import GraphConstruction.constants as constants

def almost_equal(x, y, e):
    return abs(x - y) <= e

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

    def test_constraint(self):
        # Create directed graph with edges from E
        E = [(0, 1), (1, 2), (1, 0), (2, 3), (3, 0)]
        G = networkx.DiGraph()
        for e in E:
            G.add_edge(e[0], e[1])
        graph = Monoplex(G, True, None)
        graph.computeConstraint()
        assert almost_equal(graph.constraint[0], 0.555555, constants.EPS)
        assert almost_equal(graph.constraint[1], 0.555555, constants.EPS)
        assert almost_equal(graph.constraint[2], 0.5, constants.EPS)
        assert almost_equal(graph.constraint[3], 0.5, constants.EPS)


    def test_effectiveSize(self):
        # Create directed graph with edges from E
        E = [(0, 1), (1, 2), (1, 0), (2, 3)]
        G = networkx.DiGraph()
        for e in E:
            G.add_edge(e[0], e[1])
        graph = Monoplex(G, True, None)
        effectiveSize = graph.computeEffectiveSize()
        assert almost_equal(effectiveSize[0], 1.0, constants.EPS)
        assert almost_equal(effectiveSize[1], 2.0, constants.EPS)
        assert almost_equal(effectiveSize[2], 2.0, constants.EPS)
        assert (math.isnan(effectiveSize[3]))

    # TODO add test for the rest of measures

if __name__ == '__main__':
    unittest.main()
