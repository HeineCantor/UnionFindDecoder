import stim
import utils
import pymatching
import numpy as np

from utils import countLogicalErrors, countLogicalErrors_uf, countLogicalErrors_uf_rotated

ROUNDS = 11
DISTANCE = 11

SAMPLING_SHOTS = 5000

if __name__ == "__main__":
    code = stim.Circuit.generated(
        "surface_code:unrotated_memory_z",
        rounds=ROUNDS,
        distance=DISTANCE,
        before_round_data_depolarization=0.02,
        before_measure_flip_probability=0,
    )

    detectorErrorModel = code.detector_error_model()
    detCoords = detectorErrorModel.get_detector_coordinates()

    #numLogicalErrors = countLogicalErrors_uf(code, SAMPLING_SHOTS)
    numLogicalErrors = countLogicalErrors_uf_rotated(code, SAMPLING_SHOTS)

    print(f"Number of logical errors: {numLogicalErrors}")
    print(f"Error rate: {numLogicalErrors / SAMPLING_SHOTS * 100}%")
