import infoFlowNetwork
from scipy.stats import spearmanr

# InformationFlowNetwork which computes the correlation for the 2path rankings of nodes for the
# network with and without transitive faults.
class OrderInfoFlowNetwork(infoFlowNetwork.InformationFlowNetwork):
    '''
            Returns the list of nodes in the netw-th network, sorted in increasing order by the number of
            2-paths for each node. id represents the type of network (0 = without transitive faults,
            1 = with optimistic transitive faults, 2 =  with pessimistic transitive faults.)
        '''

    def getNodesOrder(self, id, netw, netwType):
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

    def getNodesOrderAggregate(self, id, netwType):
        centralityList = []
        for nod in self.nr2p[netwType][id]:
            centralityList.append((self.nr2p[netwType][id][nod], nod))
        centralityList = sorted(centralityList, reverse=True)
        order = []
        top10P = len(centralityList) // 10
        for p in centralityList:
            top10P -= 1
            # if top10P < 0:
            #     break
            order.append(p[1])
            if len(order) > 1:
                assert (self.nr2p[netwType][id][order[-1]] <= self.nr2p[netwType][id][order[-2]])

        return order

    '''
        For the current delta_t time interval, compute the number of 2-paths for each node in the
        aggregate network as the sum of the number of 2-paths of the node in each network.
    '''
    def compute2PathsAggregateNetwork(self, netwType):
        for netw in range(1, self.nrGraphs + 1):
            if not (netw in self.nr2paths[netwType][0]):
                continue
            atLeastOne2P = False
            for nod in self.nr2paths[netwType][0][netw]:
                if self.nr2paths[netwType][0][netw][nod] > 0:
                    atLeastOne2P = True
                    break
            # if atLeastOne2P == False:
            #     continue
            for nod in self.nr2paths[netwType][0][netw]:
                for i in range(3):
                    if not (nod in self.nr2p[netwType][i]):
                        self.nr2p[netwType][i][nod] = 0
                    self.nr2p[netwType][i][nod] += self.nr2paths[netwType][i][netw][nod]

    def computeUpperLowerAggregateNetwork(self, netwType):
        self.compute2PathsAggregateNetwork(netwType)
        N = len(self.nr2p[netwType][0])
        optTfs = 0
        pessTfs = 0
        nr2ps = 0
        sumO = 0
        sumP = 0
        okN = 0
        for a in self.nr2p[netwType][0]:
            if self.nr2p[netwType][0][a] > 0:
                okN += 1
                optTfs += self.nr2p[netwType][0][a] - self.nr2p[netwType][1][a]
                pessTfs += self.nr2p[netwType][0][a] - self.nr2p[netwType][2][a]
                nr2ps += self.nr2p[netwType][0][a]
                sumO += (self.nr2p[netwType][0][a] - self.nr2p[netwType][1][a]) / self.nr2p[netwType][0][a]
                sumP += (self.nr2p[netwType][0][a] - self.nr2p[netwType][2][a]) / self.nr2p[netwType][0][a]
        sumO /= okN
        sumP /= okN
        #self.crtResult[netwType][0] = (round(sumO, 4), round(sumP, 4))
        print('For aggregate netw,', netwType, 'we have', sumO, sumP, okN, nr2ps, optTfs / nr2ps, pessTfs / nr2ps)

    def getRanginkCorrelation(self, netwType):
        Order = [[], [], []]
        for netw in range(1, self.nrGraphs + 1):
            order = []
            for i in range(3):
                order.append(self.getNodesOrder(i, netw, netwType))
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

    def getRanginkCorrelationAggregate(self, netwType):
        self.compute2PathsAggregateNetwork(netwType)
        order = []
        for i in range(3):
            order.append(self.getNodesOrderAggregate(i, netwType))

        w, p = spearmanr(order[0], order[1])
        self.crtResult[netwType][1] = (round(w, 4), p)
        # print(w, p)
        w, p = spearmanr(order[0], order[2])
        self.crtResult[netwType][2] = (round(w, 4), p)
        # print(w, p)
