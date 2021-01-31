import unittest
# some_file.py
import sys
sys.path.insert(1, 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction')
# sys.path.insert(2, 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\reproValidity.py')
import reproValidity

# from GraphConstruction.reproValidity import *

def almost_equal(x, y, e):
    return abs(x - y) <= e

class TestInfoFlowNetwork(reproValidity.InformationFlowNetwork):
    def __init__(self, msgDict, delta_t, t, minTime):
        super().__init__(msgDict, delta_t, t, minTime)

    def addHuman(self, name, nrNodes):
        if not (name in self.humanDict):
            nrNodes += 1
            self.Label[nrNodes] = name
            self.humanDict[name] = nrNodes
        return nrNodes

def createInfoFlowNetwork(t, delta_t, minTime, msgDict, msgEdgesFilePath):
    infoFlowNetwork = TestInfoFlowNetwork(msgDict, delta_t, t, minTime)
    nrNodes = infoFlowNetwork.readMsgEdges(0, msgEdgesFilePath)
    return infoFlowNetwork

def testNr2Paths(infoFlowNetwork, netwType, resFilePath):
    f = open(resFilePath, "r")
    while True:
        crtL = f.readline().split()
        if not crtL:
            break
        nod = infoFlowNetwork.humanDict[crtL[0]]
        netw = int(crtL[1])

        for index in range(3):
            val = 0
            if nod in infoFlowNetwork.nr2paths[netwType][index][netw]:
                val = infoFlowNetwork.nr2paths[netwType][index][netw][nod]
            assert int(crtL[index + 2]) == val
    f.close()

class TestValidity(unittest.TestCase):
    def testMonoplex(self):
        msgDetailsFilePath = 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\msgDetailsTest2.txt'
        minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)
        t = '1 hour'
        delta_t = 3600
        msgEdgesFilePath = 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\msgEdgesTest1.txt'
        infoFlowNetwork = createInfoFlowNetwork(t, delta_t, minTime, msgDict, msgEdgesFilePath)
        netwType = 'monoplex'
        infoFlowNetwork.getTransitiveFault(netwType)
        resFilePath = 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\monoplexRes1.txt'
        testNr2Paths(infoFlowNetwork, netwType, resFilePath)

    def testMLN(self):
        msgDetailsFilePath = 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\msgDetailsTest2.txt'
        minTime, maxTime, msgDict = reproValidity.readMsgDetails(msgDetailsFilePath)
        t = '1 hour'
        delta_t = 3600
        msgEdgesFilePath = 'D:\\AKwork2020-2021\\Higher-Dimensions\\GraphConstruction\\Data\\msgEdgesTest1.txt'
        infoFlowNetwork = createInfoFlowNetwork(t, delta_t, minTime, msgDict, msgEdgesFilePath)
        infoFlowNetwork.getTransitiveFault('MLN')


if __name__ == '__main__':
    unittest.main()
