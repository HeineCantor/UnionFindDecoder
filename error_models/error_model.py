from abc import ABC

class ErrorModel(ABC):
    def __init__(self, error_rate : float = 0.01):
        self.error_rate = error_rate

    def getAfterResetErrorRate(self) -> float:
        raise NotImplementedError
    
    def getBeforeMeasurementErrorRate(self) -> float:
        raise NotImplementedError
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        raise NotImplementedError
    
    def getCliffordErrorRate(self) -> float:
        raise NotImplementedError
    
