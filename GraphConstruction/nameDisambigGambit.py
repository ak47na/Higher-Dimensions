import pandas as pd
import disambigGambit
import disambigBird

def getEnronDf():
    filePath = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\\emails.csv'
    df = pd.read_csv(filePath)
    return df

def getNameAndEmailListsEnron(df):
    colNames = df.columns
    aliasNames = {}
    aliasNamesList = []
    aliasEmails = {}
    aliasEmailsList = []
    noRows = 0
    for index, row in df.iterrows():
        noRows += 1
        messageList = row[colNames[1]].split('\n')
        crtEmail = ''
        crtName = ''
        for ln in messageList:
            if 'From:' in ln[:6]:
                if crtEmail == '':
                    crtEmail = ln[6:]
            elif 'X-From: ' in ln[:8]:
                crtName = ln[8:]
        if not(crtEmail in aliasEmails) or not(crtName in aliasNames):
            aliasNamesList.append(crtName)
            aliasEmailsList.append(crtEmail)
            aliasNames[crtName] = True
            aliasEmails[crtEmail] = True

    print(noRows, len(aliasNames), len(aliasEmails))
    return aliasNamesList, aliasEmailsList


def getNameAndEmailLists():
    f = open(r"D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apachePeople.txt", 'r', encoding="utf-8")
    aliasNames = []
    aliasEmails = []
    while True:
        crtLine = f.readline()
        if not crtLine:
            break
        crtLine = crtLine.replace('\n', '').split('/\\')
        aliasNames.append(crtLine[0])
        aliasEmails.append(crtLine[1])
    return aliasNames, aliasEmails

def disambigApache():
    aliasNames, aliasEmails = getNameAndEmailLists()
    aliases = pd.DataFrame({'rec_name': aliasNames, 'rec_email': aliasEmails})
    birdFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheAliasesBird2.csv'
    gambitFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\apacheAliasesGambit2.csv'
    authors1 = disambigBird.disambiguate_authors_BIRD(aliases)
    print(authors1)
    authors2 = disambigGambit.disambiguate_authors_GAMBIT(aliases)
    print(authors2)
    authors1.to_csv(birdFilePath)
    authors2.to_csv(gambitFilePath)

def disambigEnron():
    aliasNames, aliasEmails = getNameAndEmailListsEnron(getEnronDf())
    aliases = pd.DataFrame({'rec_name': aliasNames, 'rec_email': aliasEmails})
    gambitFilePath = r'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\enronAliasesGambit.csv'
    authors1 = disambigBird.disambiguate_authors_BIRD(aliases)
    print(authors1)
    authors1.to_csv(gambitFilePath)

disambigEnron()
