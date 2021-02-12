import mailID
import parameters
import infoFlowNetwork

from datetime import datetime
from networkx import *
from scipy.stats import spearmanr
from math import *

class AdvMultilayeredNetwork(infoFlowNetwork.InformationFlowNetwork):
    def countCase1(self, netw, a, b, c, cleAtoBup):
        if (self.inLayer[netw][a][b][0] < self.inLayer[netw][b][c][1]) and cleAtoBup:
            self.case[0] += 1

    def countCase2(self, netw, a, b, c, cleAdowntoB):
        if self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1] and cleAdowntoB:
            if (self.crossLayerIn[netw][b][a][0] < self.inLayer[netw][b][c][1]):
                self.case[1] += 1

    def countCase3(self, netw, a, b, c, cleBtoupC):
        if self.inLayer[netw][a][b][0] > self.inLayer[netw][b][c][1] and cleBtoupC:
            self.case[2] += 1

    def countCase4(self, netw, a, b, c, cleBdowntoC):
        if self.inLayer[netw][a][b][1] < self.inLayer[netw][b][c][0] and cleBdowntoC:
            if self.crossLayerIn[netw][c][b][0] < self.inLayer[netw][a][b][1]:
                self.case[3] += 1


    def countSpCases(self):
        self.case = [0, 0, 0, 0, 0]
        for netw in range(1, self.nrGraphs + 1):
            N = len(self.inLayer[netw])
            if N == 0:
                continue
            for a in self.inLayer[netw]:
                for b in self.inLayer[netw][a]:
                    if a in self.crossLayerIn[netw]:
                        self.case[4] += len(self.crossLayerIn[netw][a])
                    if not (b in self.inLayer[netw]):
                        # Ignore a's neighbours with out-degree = 0.
                        continue
                    for c in self.inLayer[netw][b]:
                        cleAdowntoB = b in self.crossLayerIn[netw] and a in self.crossLayerIn[netw][b]
                        cleAtoBup = a in self.crossLayerOut[netw] and b in self.crossLayerOut[netw][a]
                        cleBtoupC = b in self.crossLayerOut[netw] and c in self.crossLayerOut[netw][b]
                        cleBdowntoC = c in self.crossLayerIn[netw] and b in self.crossLayerIn[netw][c]

                        self.countCase1(netw, a, b, c, cleAtoBup)
                        self.countCase2(netw, a, b, c, cleAdowntoB)
                        self.countCase3(netw, a, b, c, cleBtoupC)
                        self.countCase4(netw, a, b, c, cleBdowntoC)
