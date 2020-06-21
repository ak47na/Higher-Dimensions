import plotly.graph_objects as go
from Sample import *

def getData(s):
    data = []
    nodeTypes = []
    count = s.getCountOfNodesPerLayer()
    nodeTypes = [*count]
    print(nodeTypes)
    nrRows = len(nodeTypes)
    nrColumns = s.getNrLayers()
    countPerLayer = []
    for rowId in range(nrRows):
        key = nodeTypes[rowId]
        lst = []
        for val in count[key]:
            lst.append(val)
        countPerLayer.append(lst)

    data.append(nodeTypes)
    for i in range(nrColumns):
        lst = []
        for j in range(nrRows):
            lst.append(countPerLayer[j][i])
        data.append(lst)

    return data
def addNodeType(nodeTypes, nrNodeTypes, nod):
    if not (nod in nodeTypes):
        nodeTypes[nod] = nrNodeTypes
        nrNodeTypes += 1
    return nrNodeTypes
def createLayerTable(layer, edgeTy):
    nodeTypes = {}
    nrNodeTypes = 0
    vals = {}
    for e in edgeTy:
        nrNodeTypes = addNodeType(nodeTypes, nrNodeTypes, e[0])
        nrNodeTypes = addNodeType(nodeTypes, nrNodeTypes, e[1])
        if not ((nodeTypes[e[0]], nodeTypes[e[1]]) in vals):
            vals[(nodeTypes[e[0]], nodeTypes[e[1]])] = 0
        if not ((nodeTypes[e[1]], nodeTypes[e[0]]) in vals):
            vals[(nodeTypes[e[1]], nodeTypes[e[0]])] = 0
        vals[(nodeTypes[e[0]], nodeTypes[e[1]])] += 1
        vals[(nodeTypes[e[1]], nodeTypes[e[0]])] += 1
    cols = ['Nodes in ' + layer]
    Values = []
    for key in nodeTypes:
        cols.append(key)
    Values.append(cols[1:])
    for key in nodeTypes:
        lst = []
        for i in range(nrNodeTypes):
            if not ((nodeTypes[key], i) in vals):
                lst.append(0)
            else:
                lst.append(vals[(nodeTypes[key], i)])
        Values.append(lst)
    fig = go.Figure(data=[
        go.Table(header=dict(values=cols),
                 cells=dict(values=Values))
    ])
    fig.show()


def createTable2(cols, vals):
    fig = go.Figure(data=[
        go.Table(header=dict(values=cols),
                 cells=dict(values=vals))
    ])
    fig.show()
def createTable(s):
    data = getData(s)
    fig = go.Figure(data=[
        go.Table(header=dict(values=['Layers/Nodes', 'Commiting', 'ProjectStructure', 'Reviewing', 'IssueTracking']),
                 cells=dict(values=data))
        ])
    fig.show()
