from error_models.error_model import ErrorModel

class OnlyMeasureEM(ErrorModel):
    def __init__(self, error_rate = 0.01):
        super().__init__(error_rate)
        self.name = "Only Measure EM"

    def getAfterResetErrorRate(self) -> float:
        return 0
    
    def getBeforeMeasurementErrorRate(self) -> float:
        return self.error_rate
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        return 0
    
    def getCliffordErrorRate(self) -> float:
        return 0