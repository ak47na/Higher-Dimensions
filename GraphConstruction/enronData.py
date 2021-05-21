import pandas as pd

def readData(filePath):
    df = pd.read_csv (filePath)
    print(df.columns)
    print(df.at[0, 'message'].split('\n'))



readData('D:\AKwork2021\HigherDimensions\Higher-Dimensions\\emails.csv')