from error_models.error_model import ErrorModel

class WillowEM(ErrorModel):
    # Reference: https://quantumai.google/static/site-assets/downloads/willow-spec-sheet.pdf
    def __init__(self):
        self.name = "Willow EM"
        self.single_qubit_gate_error_rate = 0.00035 # 0.035%
        self.two_qubit_gate_error_rate = 0.0033 # 0.33%
        self.measurement_error_rate = 0.0077 # 0.77%
        self.reset_error_rate = 0 # 0% -> leakage controlled
        self.error_rate = self.two_qubit_gate_error_rate

    def getAfterResetErrorRate(self) -> float:
        return self.reset_error_rate
    
    def getBeforeMeasurementErrorRate(self) -> float:
        return self.measurement_error_rate
    
    def getBeforeRoundDataDepolarizationErrorRate(self) -> float:
        return 0
    
    def getCliffordErrorRate(self) -> float:
        return self.two_qubit_gate_error_rate