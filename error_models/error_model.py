from abc import ABC

class ErrorModel(ABC):
    """
    An abstract base class representing an error model.

    Attributes
    ----------
    reset_error : float
        The probability of resetting to the orthogonal state (i.e. resetting to |1> instead of |0>). 
    measurement_error : float
        The probability of flipping the measurement outcome.
    one_qubit_gate_error : float
        The probability of a 1-qubit gate to be followed by depolarizing error (i.e. applying one from {X, Y, Z}).
    two_qubit_gate_error : float
        The probability of a 2-qubit gate to be followed by depolarizing error (i.e. applying one from {X, Y, Z, I}^2 except {II}).
    phenomenological_error : float
        The probability of a phenomenological error (i.e. applying one from {X, Y, Z} at each round to qubits).
        
    name : str
        The name of the error model (for display purpose).

    Methods
    -------
    toStim()
        Convert the error model to a Stim error model.
    """
    def __init__(self):
        self.reset_error = 0.0
        self.measurement_error = 0.0
        self.one_qubit_gate_error = 0.0
        self.two_qubit_gate_error = 0.0
        self.phenomenological_error = 0.0

        self.name = None

    def toStim(self):
        """
        Convert the error model to a Stim error model.

        Returns
        -------
        dict
            A dictionary representing the error model in Stim format.
        """
        return {
            "before_round_data_depolarization": 0,
            "before_measure_flip_probability": 0,
            "after_clifford_depolarization": 0,
            "after_reset_flip_probability": 0,
        }
    
