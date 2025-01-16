from surface_code import SurfaceCode, EdgeStatus

DISTANCE = 3

def unionFindZ(code : SurfaceCode):
    zRootList = code.getDefianceZ()

    support = code.getSupport()
    fusionList = []

    print(support)

    for root in zRootList:
        edgeList = []

        iUpper, jUpper, upperExists = getZUpperEdge(root[0], root[1], code.size[0])
        if upperExists:
            edgeList.append((iUpper, jUpper))

        iRight, jRight, rightExists = getZRightEdge(root[0], root[1], code.size[0])
        if rightExists:
            edgeList.append((iRight, jRight))

        iLeft, jLeft, leftExists = getZLeftEdge(root[0], root[1], code.size[0])
        if leftExists:
            edgeList.append((iLeft, jLeft))

        iLower, jLower, lowerExists = getZLowerEdge(root[0], root[1], code.size[0])
        if lowerExists:
            edgeList.append((iLower, jLower))

        for edge in edgeList:
            if support[edge[0]][edge[1]] < EdgeStatus.GROWN:
                support[edge[0]][edge[1]] += 1
                if support[edge[0]][edge[1]] == EdgeStatus.GROWN:
                    fusionList.append(edge)
    
    print(support)
    print(fusionList)

def getZUpperEdge(i, j, distance):
    exists = True
    return 2*i, j, exists

def getZRightEdge(i, j, distance):
    exists = j < distance - 1
    return 2*i+1, j, exists

def getZLeftEdge(i, j, distance):
    exists = j > 0
    return 2*i+1, j-1, exists

def getZLowerEdge(i, j, distance):
    exists = True
    return 2*i+2, j, exists

testCode = SurfaceCode(distance=DISTANCE, px_error=0.1, pz_error=0.1, meas_error=0.1)
print(testCode)

print("\nGenerating single round error:")
testCode.generateError()
print(testCode)

unionFindZ(testCode)