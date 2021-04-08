import pandas as pd

import disambigGambit
import disambigBird

aliasNames = []
aliasEmails = []

def getNameAndEmailDF():
    f = open(r"D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apachePeople.txt", 'r', encoding="utf-8")
    while True:
        crtLine = f.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '').split('/\\')
        aliasNames.append(crtLine[0])
        aliasEmails.append(crtLine[1])

getNameAndEmailDF()
aliases = pd.DataFrame({'rec_name': aliasNames, 'rec_email': aliasEmails})
birdFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheAliasesBird2.csv'
gambitFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheAliasesGambit2.csv'
authors1 = disambigBird.disambiguate_authors_BIRD(aliases)
print(authors1)
authors2 = disambigGambit.disambiguate_authors_GAMBIT(aliases)
print(authors2)
authors1.to_csv(birdFilePath)
authors2.to_csv(gambitFilePath)