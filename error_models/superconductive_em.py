from error_models.error_model import ErrorModel

# Reference: https://arxiv.org/pdf/2409.14765
class SuperconductiveEM(ErrorModel):
    def __init__(self, base_error_rate = 0.01):
        super().__init__()
        self.name = f"SI1000 EM ({base_error_rate})"

        self.reset_error = 2 * base_error_rate
        self.measurement_error = 5 * base_error_rate
        self.one_qubit_gate_error = base_error_rate / 10
        self.two_qubit_gate_error = base_error_rate

        self.idle_during_gates_on_other_qubits = base_error_rate / 10
        self.idle_during_reset_on_other_qubits = 2 * base_error_rate
        self.idle_during_measurement_on_other_qubits = 2 * base_error_rate

    def toStim(self):
        return {
            "before_round_data_depolarization": 0,  # Not a phenomenological error model
            "before_measure_flip_probability": self.idle_during_measurement_on_other_qubits,
            "after_clifford_depolarization": self.two_qubit_gate_error, # Stim.generated handles one_qubit_errors the same as two_qubit_errors
            "after_reset_flip_probability": self.idle_during_reset_on_other_qubits,
        }