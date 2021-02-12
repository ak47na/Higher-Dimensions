import mailID
import constants
import reproValidity
import infoFlowNetwork
from scipy.stats import spearmanr
from math import *

# InformationFlowNetwork which computes the correlation for the 2path rankings of nodes for the
# network with and without transitive faults.
class OrderInfoFlowNetwork(infoFlowNetwork.InformationFlowNetwork):
    '''
            Returns the list of nodes in the netw-th network, sorted in increasing order by the number of
            2-paths for each node. id represents the type of network (0 = without transitive faults,
            1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
        '''

    def getNodesOrder(self, id, netw):
        netwType = 'monoplex'
        centralityList = []
        for nod in self.nr2paths[netwType][id][netw]:
            centralityList.append((self.nr2paths[netwType][id][netw][nod], nod))
        centralityList = sorted(centralityList)
        order = []
        for p in centralityList:
            order.append(p[1])
        return order

    '''
        Returns the list of nodes in the aggregate network, sorted in increasing order by the number of
        2-paths for each node. id represents the type of network (0 = without transitive faults, 
        1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
    '''

    def getNodesOrderAggregate(self, id):
        centralityList = []
        for nod in self.nr2p[id]:
            centralityList.append((self.nr2p[id][nod], nod))
        centralityList = sorted(centralityList)
        order = []
        for p in centralityList:
            order.append(p[1])
            if len(order) > 1:
                assert (self.nr2p[id][order[-1]] >= self.nr2p[id][order[-2]])

        return order

    '''
        For the current delta_t time interval, compute the number of 2-paths for each node in the
        aggregate network as the sum of the number of 2-paths of the node in each network.
    '''

    def compute2PathsAggregateNetwork(self):
        netwType = 'monoplex'
        for netw in range(1, self.nrGraphs + 1):
            if not (netw in self.nr2paths[netwType][0]):
                continue
            for nod in self.nr2paths[netwType][0][netw]:
                if not (nod in self.nr2p[0]):
                    for i in range(3):
                        self.nr2p[0][nod] = 0
                        self.nr2p[1][nod] = 0
                        self.nr2p[2][nod] = 0
                for i in range(3):
                    self.nr2p[i][nod] += self.nr2paths[netwType][i][netw][nod]

    def getRanginkCorrelation(self):
        netwType = 'monoplex'
        Order = [[], [], []]
        for netw in range(1, self.nrGraphs + 1):
            order = []
            for i in range(3):
                order.append(self.getNodesOrder(i, netw))
                for x in order[i]:
                    Order[i].append(x)
        w, p = spearmanr(Order[0], Order[1])
        self.crtResult[netwType][1] = (w, p)
        # print(w, p)
        w, p = spearmanr(Order[0], Order[2])
        # print(w, p)
        self.crtResult[netwType][2] = (w, p)

    '''
        Returns the Spearman rank correlation value between the 2-path ranking of the nodes in the
        network with transitive faults with the 2-path ranking of the nodes in the network without 
        transitive faults.
    '''

    def getRanginkCorrelationAggregate(self):
        netwType = 'monoplex'
        self.compute2PathsAggregateNetwork()
        order = []
        for i in range(3):
            order.append(self.getNodesOrderAggregate(i))
        w, p = spearmanr(order[0], order[1])
        self.crtResult[netwType][1] = (w, p)
        # print(w, p)
        w, p = spearmanr(order[0], order[2])
        self.crtResult[netwType][2] = (w, p)
        # print(w, p)
