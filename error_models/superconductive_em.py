from error_models.error_model import ErrorModel

# Reference: https://arxiv.org/pdf/2409.14765
class SuperconductiveEM(ErrorModel):
    def __init__(self, error_rate = 0.01):
        super().__init__(error_rate)
        self.name = "Superconductive EM"

    def getAfterResetErrorRate(self) -> float:
        return 2 * self.error_rate
    
    def getBeforeMeasurementErrorRate(self) -> float:
        return 5 * self.error_rate
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        return 0
    
    def getCliffordErrorRate(self) -> float:
        return self.error_rate