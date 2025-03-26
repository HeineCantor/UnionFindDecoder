from abc import ABC

# TODO: generalizzare su error model extra-Stim, + eventuali funzioni di conversione toStim()
class ErrorModel(ABC):
    def __init__(self, error_rate : float = 0.01):
        self.error_rate = error_rate
        self.name = None

    def getAfterResetErrorRate(self) -> float:
        raise NotImplementedError
    
    def getBeforeMeasurementErrorRate(self) -> float:
        raise NotImplementedError
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        raise NotImplementedError
    
    def getCliffordErrorRate(self) -> float:
        raise NotImplementedError
    
