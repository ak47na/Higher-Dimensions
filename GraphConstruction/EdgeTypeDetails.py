LayerPerm = [0, 1, 2, 3, 4]
LayerName = [0, 'Committing', 'Project Structure', 'Reviewing', 'Issue Tracking']
def getLayerName():
    names = [0]
    for i in range(1, 5):
        names.append(LayerName[LayerPerm[i]])
    return names
def getLayerPerm():
    return LayerPerm
def getEdgeTypeDetails_util():
    EdgeTypeDetails = [(0, 0, 0)] * 18
    EdgeTypeDetails[1] = (2, 'file', 'file')
    EdgeTypeDetails[2] = ((1, 2), 'C', 'R')
    EdgeTypeDetails[3] = (1, 'file', 'file')
    EdgeTypeDetails[4] = (1, 'C', 'file')
    EdgeTypeDetails[5] = (4, 'I_A', 'issue')
    EdgeTypeDetails[6] = (4, 'I_R', 'issue')
    EdgeTypeDetails[7] = (4, 'I_R', 'I_R')
    EdgeTypeDetails[8] = (3, 'R', 'R')
    # 9 is for alias edges
    EdgeTypeDetails[10] = (3, 'R', 'file')
    EdgeTypeDetails[11] = EdgeTypeDetails[10]
    EdgeTypeDetails[12] = (4, 'file', 'issue')
    EdgeTypeDetails[13] = (1, 'C', 'C')
    EdgeTypeDetails[14] = (1, 'C', 'file')  # ownership
    EdgeTypeDetails[15] = (4, 'issue', 'issue')
    EdgeTypeDetails[16] = (3, 'R', 'R\'')
    EdgeTypeDetails[17] = ((3, 1), 'R\'', 'issue')
    return EdgeTypeDetails
def getEdgeTypeDetails():
    edges = getEdgeTypeDetails_util()
    newEdges = []
    for edge in edges:
        if isinstance(edge[0], int):
            newEdges.append((LayerPerm[edge[0]], edge[1], edge[2]))
        else:
            newEdges.append(((LayerPerm[edge[0][0]], LayerPerm[edge[0][1]]), edge[1], edge[2]))
    return newEdges
