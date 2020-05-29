import csv
import pandas as pd

#Jar[file_Name('.java/.class' without extension)] = jar name
Jar = {}
file1 = open("\\extractedJars.txt","r")
fileW = []
fileW.append(open("\\ClassDep.txt", "w"))
fileW.append(open("\\FileDep.txt", "w"))

def addEdge(sA, sB, isFile):
    msg = 'ClassEdge '
    if isFile:
        msg = 'FileEdge '
    fileW[isFile].write(msg + sA + ' ' + sB + '\n')
    if sA in Jar:
        fileW[isFile].write(msg + Jar[sA] + ' ' + sB + '\n')
    if sB in Jar:
        fileW[isFile].write(msg + sA + ' ' + Jar[sB] + '\n')
        if sA in Jar:
            fileW[isFile].write(msg + Jar[sA] + ' ' + sB + '\n')

def Str(A):
    sA = ''
    for i in range(3, len(A) - 2):
        sA += A[i] + '.'
    sA += A[len(A) - 2]
    return sA

while True:
    crtL = file1.readline()
    if not crtL:
        break
    dep = crtL.split(" : ")
    if len(dep) < 2:
        continue
    s1 = dep[0].replace('/', '.').replace('\\', '.').rsplit('.', 1)
    s2 = dep[1].replace('/', '.').replace('\\', '.').replace('\n', '')
    Jar[s1[0]] = s2.rsplit('.', 1)[0]

with open('\\eclipseRepo_FileDependenciesNS.csv', 'r') as file:
    reader = csv.reader(file)
    col_names = []
    for row in reader:
       col_names = row
       break
    df = pd.read_csv("\\eclipseRepo_FileDependenciesNS.csv", usecols=col_names)
    for ind in df.index:
        A = df[col_names[0]][ind].replace('\\', '.').split('.')
        B = df[col_names[1]][ind].replace('\\', '.').split('.')
        sA = Str(A).replace('\n', '')
        sB = Str(B).replace('\n', '')
        addEdge(sA, sB, 1)

with open('\\eclipseRepo_ClassDependenciesNS.csv', 'r') as file:
    reader = csv.reader(file)
    col_names = []
    for row in reader:
       col_names = row
       break
    df = pd.read_csv("\\eclipseRepo_ClassDependenciesNS.csv", usecols=col_names)
    for ind in df.index:
        sA = df[col_names[0]][ind].replace('\\', '.').replace('\n', '')
        sB = df[col_names[1]][ind].replace('\\', '.').replace('\n', '')
        addEdge(sA, sB, 0)

file1.close()
fileW[0].close()
fileW[1].close()
