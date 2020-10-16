class Edge:
    def __init__(self, nod1_, layer1_, nod2_, layer2_, color_):
        self.nod1 = nod1_
        self.layer1 = layer1_
        self.nod2 = nod2_
        self.layer2 = layer2_
        self.color = color_

    def __lt__(self, other):
        if self.layer1 == other.layer1 and self.layer2 == other.layer2:
            if self.nod1 == other.nod1:
                return self.nod2 < other.nod2
            return self.nod1 < other.nod1
        if self.layer1 == other.layer1:
            return self.layer2 < other.layer2
        return self.layer1 < other.layer1

    def __hash__(self):
        return hash((self.nod1, self.layer1, self.nod2, self.layer2, self.color))

    def __eq__(self, other):
        return ((self.nod1, self.layer1, self.nod2, self.layer2, self.color) == (
        other.nod1, other.layer1, other.nod2, other.layer2, other.color))

    def __ne__(self, other):
        return not (self == other)

    def ToString(self):
        edge = str(self.nod1) + ' ' + str(self.layer1) + ' ' + str(self.nod2) + ' ' + str(self.layer2)
        return edge
