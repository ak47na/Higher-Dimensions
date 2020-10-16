class File:
    def __init__(self, index_, name_, complexity_, churn_, size_, sizeSum_):
        self.index = index_
        self.name = name_
        self.updateMeasures(complexity_, churn_, size_, sizeSum_)
    def updateMeasures(self, complexity_, churn_, size_, sizeSum_):
        self.complexity = complexity_
        self.churn = churn_
        self.size = size_
        self.sizeSum = sizeSum_

def Int(strVal):
    if strVal == '' or strVal == None:
        return -1
    return int(strVal)

def getFileName(crtL):
    crtFile = crtL.rsplit('.', 1)[0].replace("/", '.')
    return crtFile

def readFileMeasures(fileDict, readFileName):
    f = open(readFileName, "r")
    files = []
    posInFiles = {}
    while True:
        crtL = f.readline()
        if not crtL:
            break
        lst = crtL.split('/\\')
        fileName = getFileName(lst[0])
        if not (fileName in fileDict):
            continue
        fileID = fileDict[getFileName(lst[0])]
        complexity = Int(lst[1])
        churn = Int(lst[2])
        size = Int(lst[3])
        sizeSum = Int(lst[4])
        files.append(File(fileID, fileName, complexity, churn, size, sizeSum))
        posInFiles[fileID] = len(files) - 1
    return files, posInFiles
