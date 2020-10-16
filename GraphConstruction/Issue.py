from datetime import *

f = open("Data//ver.txt", "r")
Time = {}
while True:
    crtL = f.readline()
    if not crtL:
        break
    lst = crtL.split('/\\')
    #convert to dt pair
    lst[1] = lst[1][:-1]

    Time[lst[0]] = datetime.strptime(lst[1], '%d %B %Y')

def getPrefVersion(version):
    lst = version.split('.', 2)
    return lst[0] + '.' + lst[1]
class Issue:
    def __init__(self, name_, version_, creation_ts, delta_ts, status_, res_, project_):
        self.name = name_
        self.version = getPrefVersion(version_)
        self.creation_ts = creation_ts
        self.delta_ts = delta_ts
        self.status = status_
        self.res = res_
        self.project = project_
        self.iType = self.getType()
    def setIndex(self, index_):
        self.index = index_
    def getType(self):
        if not (str(self.version) in Time):
            print('Error')
            exit()
        if Time[str(self.version)] < self.delta_ts:
            return 'post-release'
        return 'pre-release'