from datetime import *

f = open("ver.txt", "r")
Time = {}
while True:
    crtL = f.readline()
    if not crtL:
        break
    lst = crtL.split('/\\')
    #convert to dt pair
    Time[lst[0]] = (datetime.strptime(lst[1], '%Y-%m-%d'), datetime.strptime(lst[2], '%Y-%m-%d'))

class Issue:
    def __init__(self, name_, version_, creation_ts, delta_ts, status_, res_, project_):
        self.name = name_
        self.version = version_
        self.creation_ts = creation_ts
        self.delta_ts = delta_ts
        self.status = status_
        self.res = res_
        self.project = project_
        self.iType = self.getType()
    def setIndex(self, index_):
        self.index = index_
    def getType(self):
        if Time[str(self.project) + str(self.version)][1] < self.delta_ts:
            return 'post-release'
        return 'pre-release'
