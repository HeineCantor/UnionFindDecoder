from error_models.error_model import ErrorModel

class PhenomenologicalEM(ErrorModel):
    def __init__(self, base_error_rate = 0.01):
        super().__init__()
        self.name = f"Phenomenological EM ({base_error_rate})"
        
        self.phenomenological_error = base_error_rate

    def toStim(self):
        return {
            "before_round_data_depolarization": self.phenomenological_error, # Exclusively a phenomenological error model
            "before_measure_flip_probability": 0,
            "after_clifford_depolarization": 0,
            "after_reset_flip_probability": 0,
        }