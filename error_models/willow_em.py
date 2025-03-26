from error_models.error_model import ErrorModel

class WillowEM(ErrorModel):
    # Reference: https://quantumai.google/static/site-assets/downloads/willow-spec-sheet.pdf
    def __init__(self):
        self.name = "Willow EM"

        self.reset_error = 0 # 0% -> leakage controlled
        self.measurement_error = 0.0077
        self.one_qubit_gate_error = 0.00035
        self.two_qubit_gate_error = 0.0033

    def toStim(self):
        return {
            "before_round_data_depolarization": 0, # Not a phenomenological error model
            "before_measure_flip_probability": self.measurement_error,
            "after_clifford_depolarization": self.two_qubit_gate_error, # Stim.generated handles one_qubit_errors the same as two_qubit_errors
            "after_reset_flip_probability:": self.reset_error
        }