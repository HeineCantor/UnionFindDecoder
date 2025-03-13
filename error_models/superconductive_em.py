from error_models.error_model import ErrorModel

# Reference: https://arxiv.org/pdf/2409.14765
class SuperconductiveEM(ErrorModel):
    def getAfterResetErrorRate(self) -> float:
        return 2 * self.error_rate
    
    def getBeforeMeasurementErrorRate(self) -> float:
        return 5 * self.error_rate
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        return 0
    
    def getCliffordErrorRate(self) -> float:
        return self.error_rate