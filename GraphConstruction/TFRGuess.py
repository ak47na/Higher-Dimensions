import infoFlowNetwork
import correlationValidity
from scipy.stats import spearmanr

# InformationFlowNetwork which computes the TFR using different guesses.
class TFRGuessInfoFlowNetwork(correlationValidity.OrderInfoFlowNetwork):
    def getAlpha2Guess(self, ty):
        twoPaths = [{}, {}]
        tfaults = [[{}, {}], [{}, {}]]
        for bucket in self.allTimesBucket[1]:
            netw = self.timeDict[bucket]
            for a in self.allTimesBucket[1][bucket]:
                for b in self.allTimesBucket[1][bucket][a]:
                    if a == b or not (b in self.allTimesBucket[1][bucket]):
                        continue
                    if not (b in twoPaths[0]):
                        for i in range(2):
                            twoPaths[i][b] = {}
                            tfaults[i][0][b] = {}
                            tfaults[i][1][b] = {}
                    if (bucket in self.allTimesBucket[ty]) and (a in self.allTimesBucket[ty][bucket]) and (b in self.allTimesBucket[ty][bucket][a])\
                            and (b in self.allTimesBucket[ty][bucket]):
                        twoPaths[0], tfaults[0] = self.updateTwoPaths(a, b, ty, twoPaths[0], tfaults[0], self.allTimesBucket[ty][bucket])
                    twoPaths[1], tfaults[1] = self.updateTwoPaths(a, b, 1, twoPaths[1], tfaults[1], self.allTimesBucket[1][bucket])
        if self.delta_t == 3600:
            for nod in twoPaths[0]:
                print('tps', len(twoPaths[0][nod]), nod)
        self.alpha2Guess = self.getAlphaGuessResults(twoPaths, tfaults)

    def updateTwoPaths(self, a, b, ty, twoPaths_, tfaults_, timesDict):
        for c in timesDict[b]:
            if a == c or b == c or a == b:
                continue
            twoPathTuple = (a, c)
            #assert not (twoPathTuple in twoPaths_[b])
            twoPaths_[b][twoPathTuple] = True
            if timesDict[a][b][-1][0] >= timesDict[b][c][0][0]:
                tfaults_[1][b][twoPathTuple] = True
            if timesDict[a][b][0][0] >= timesDict[b][c][-1][0]:
                tfaults_[0][b][twoPathTuple] = True
        return twoPaths_, tfaults_

    def getAlphaGuess(self, ty):
        twoPaths = [{}, {}]
        tfaults = [[{}, {}], [{}, {}]]
        for a in self.allTimes[1]:
            for b in self.allTimes[1][a]:
                if a == b or not (b in self.allTimes[1]):
                    continue
                if not (b in twoPaths[0]):
                    for i in range(2):
                        twoPaths[i][b] = {}
                        tfaults[i][0][b] = {}
                        tfaults[i][1][b] = {}
                if (a in self.allTimes[ty]) and (b in self.allTimes[ty][a]) and (b in self.allTimes[ty]):
                    twoPaths[0], tfaults[0] = self.updateTwoPaths(a, b, ty, twoPaths[0], tfaults[0], self.allTimes[ty])
                twoPaths[1], tfaults[1] = self.updateTwoPaths(a, b, 1, twoPaths[1], tfaults[1], self.allTimes[1])

        self.alphaGuess = self.getAlphaGuessResults(twoPaths, tfaults, True)

    def getAlphaGuessResults(self, twoPaths, tfaults, isAggregate = False):
        aGuess = [0, 0]
        self.getAllTFs()
        gtTP = 0
        for a in twoPaths[1]:
            gtTP += len(twoPaths[1][a])

            if isAggregate:
                assert self.gtTP[a] == len(twoPaths[1][a])
            for i in range(2):
                # for tf in tfaults[1][i][a]:
                #     if not (tf in tfaults[0][i][a]):
                #         aGuess[i] += 1
                aGuess[i] += len(tfaults[0][i][a])
                missedFlows = 0
                for twoPathTuple in twoPaths[1][a]:
                    if not (twoPathTuple in twoPaths[0][a]):
                        if not (twoPathTuple in tfaults[1][i][a]):
                            missedFlows += 1
                aGuess[i] += missedFlows
        for i in range(2):
            aGuess[i] /= gtTP
        return aGuess
