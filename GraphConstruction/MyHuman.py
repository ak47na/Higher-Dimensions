class MyHuman:
    def __init__(self, name_, index_, human_index):
        self.name = name_
        self.humanId = human_index
        self.email = None
        self.username = None
        self.isRole = [False] * 7
        self.index = index_
        self.site = 0
        # self.commits.append(commit)

    def setUserName(self, username_):
        self.username = username_

    def setRole(self, nr):
        self.isRole[nr] = True

    def setSite(self, fNr):
        self.site = Site(fNr)


def isLetter(a):
    return (ord(a) <= ord('z') and ord(a) >= ord('a'))
def purifyName(name):
    nameLen = len(name)
    newName = ''
    for i in range(nameLen):
        crtSymbol = name[i].lower()
        if isLetter(crtSymbol):
            newName += crtSymbol
    return newName
def Role(x):
    if x < 2:
        return x
    if (x == 3) or (x == 5):
        return 2
    if x == 4:
        return 3
    return x - 2
def Site(layer):
    if layer == 0 or layer == 5:
        return 0
    if layer <= 4 and layer >= 1:
        return 1
    return 2
