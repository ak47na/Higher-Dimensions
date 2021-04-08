import unicodedata

import pandas as pd

from GraphConstruction import mailClusters


def readAndWriteIdentities(readFilePath, writeFilePath):
    f = open(readFilePath, 'r', encoding="utf-8")
    g = open(writeFilePath, 'w', encoding="utf-8")
    aliases = pd.read_csv(readFilePath)
    for index, row in aliases.iterrows():
        first_i, last_i, full_i = mailClusters.purifyName(str(row['rec_name']))
        msgEmail = mailClusters.purifyEmail(str(row['rec_email']).replace(' ', ''))
        if msgEmail == '':
            msgEmail = full_i
        if full_i == '':
            full_i = msgEmail
        aliasNameEmail = msgEmail.lower() + full_i.lower()
        actualIdentity = str(row['author_id'])

        writeStr = aliasNameEmail + '/\\' + actualIdentity + '\n'
        writeStr = unicodedata.normalize('NFD', writeStr).encode('ascii', 'ignore').decode('ascii')
        g.write(writeStr.encode("utf-8", 'ignore').decode("utf-8", 'ignore'))
    g.close()
    f.close()

csvBird = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\apacheAliasesBird2.csv'
csvGambit = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\\apacheAliasesGambit2.csv'
identitiesBird = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\identityFileBird.txt'
identitiesGambit = 'D:\AKwork2021\HigherDimensions\Higher-Dimensions\ApacheData\identityFileGambit.txt'

readAndWriteIdentities(csvBird, identitiesBird)
readAndWriteIdentities(csvGambit, identitiesGambit)

