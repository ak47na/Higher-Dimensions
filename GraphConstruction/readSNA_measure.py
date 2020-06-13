import csv
import pandas as pd
import re

def readRows(reader):
    values = [0]
    for row in reader:
        vals = row[0].split(';')
        if vals[0][0] == '1':
            values.append(vals[6])
    return values

def readCsv(fileName):
    with open(fileName, 'r') as file:
        reader = csv.reader(file)
        cnt = 0
        for row in reader:
            print(row)
            col_names = row[0].split(';')
            break
        return readRows(reader)
