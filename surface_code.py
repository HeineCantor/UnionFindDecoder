import random

class EdgeStatus():
    UNOCCUPIED = 0
    HALF_GROWN = 1
    GROWN = 2

class Style():
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    PURPLE = "\033[35m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

class DataQubit:
    def __init__(self):
        self.xError = 0
        self.zError = 0

    def __str__(self):
        if self.xError == 1 and self.zError == 1:
            return f"{Style.PURPLE}Y{Style.RESET}"
        elif self.xError == 1:
            return f"{Style.RED}X{Style.RESET}"
        elif self.zError == 1:
            return f"{Style.BLUE}Z{Style.RESET}"
        else:
            return "I"
    __repr__ = __str__

class SyndromeQubit:
    def __init__(self, xSyndrome=False):
        self.value = 0
        self.xSyndrome = xSyndrome

    def __str__(self):
        if self.xSyndrome:
            return str(f"{Style.BOLD}{Style.GREEN}{self.value}\033[0m")
        else:
            return str(f"{Style.BOLD}{Style.YELLOW}{self.value}\033[0m")
    
    __repr__ = __str__

class SurfaceCode:
    def __init__(self, distance, px_error, pz_error, meas_error):
        self.initialize(distance, distance, px_error, pz_error, meas_error)

    def initialize(self, distX, distY, px_error, pz_error, meas_error):
        self.px_error = px_error
        self.pz_error = pz_error

        self.meas_error = meas_error

        self.size = (distX, distY)

        self.rowSize = 2 * distX - 1
        self.colSize = 2 * distY - 1

        self.qubits = []

        for i in range(self.rowSize):
            row = []
            for j in range(self.colSize):
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 == 1:
                    row.append(DataQubit())
                else:
                    row.append(SyndromeQubit(xSyndrome=(i % 2 == 0)))
            self.qubits.append(row)

    def generateError(self):
        for i in range(self.rowSize):
            for j in range(self.colSize):
                qubit = self.qubits[i][j]
                if isinstance(qubit, DataQubit):
                    if random.random() <= self.px_error:
                        qubit.xError ^= 1
                        if i%2==0:
                            if j>0:
                                self.qubits[i][j-1].value ^= 1
                            if j<self.colSize-1:
                                self.qubits[i][j+1].value ^= 1
                        else:
                            if i>0:
                                self.qubits[i-1][j].value ^= 1
                            if i<self.rowSize-1:
                                self.qubits[i+1][j].value ^= 1
                    if random.random() <= self.pz_error:
                        qubit.zError ^= 1
                        if i%2==0:
                            if i>0:
                                self.qubits[i-1][j].value ^= 1
                            if i<self.rowSize-1:
                                self.qubits[i+1][j].value ^= 1
                        else:
                            if j>0:
                                self.qubits[i][j-1].value ^= 1
                            if j<self.colSize-1:
                                self.qubits[i][j+1].value ^= 1

    def getDefianceX(self):
        codedX = [[qubit.value for qubit in row if isinstance(qubit, SyndromeQubit) and qubit.xSyndrome] for row in self.qubits]
        codedX = [row for row in codedX if len(row) > 0]
        # Transform in a list of coordinates
        codedX = [(i, j) for i, row in enumerate(codedX) for j, _ in enumerate(row) if row[j] == 1]
        return codedX
    
    def getDefianceZ(self):
        codedZ = [[qubit.value for qubit in row if isinstance(qubit, SyndromeQubit) and not qubit.xSyndrome] for row in self.qubits]
        codedZ = [row for row in codedZ if len(row) > 0]
        # Transform in a list of coordinates
        codedZ = [(i, j) for i, row in enumerate(codedZ) for j, _ in enumerate(row) if row[j] == 1]
        return codedZ
    
    def getSupport(self):
        support = []
        for i in range(self.rowSize):
            row = []
            for j in range(self.colSize):
                qubit = self.qubits[i][j]
                if isinstance(qubit, DataQubit):
                    row.append(EdgeStatus.UNOCCUPIED)
            support.append(row)
        return support

    def __str__(self):
        return "\n".join([str(row) for row in self.qubits])