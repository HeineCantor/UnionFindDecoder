import stim
import utils
import pymatching
import numpy as np

from utils import countLogicalErrors

ROUNDS = 31
DISTANCE = 31

SAMPLING_SHOTS = 10000

if __name__ == "__main__":
    repetitionCode = stim.Circuit.generated(
        "repetition_code:memory",
        rounds=ROUNDS,
        distance=DISTANCE,
        before_round_data_depolarization=0.13,
        before_measure_flip_probability=0.01,
    )

    # Sampling the circuit
    # sampler = repetitionCode.compile_sampler()
    # oneSample = sampler.sample(shots=1)[0]
    # for k in range(0, len(oneSample), DISTANCE-1):
    #     timeslice = oneSample[k:k+DISTANCE-1]
    #     print("[]", end="")
    #     print("[]".join("1" if e else "_" for e in timeslice), end="")
    #     print("[]")

    # Sampling the error-detecting circuit
    # detector_sampler = repetitionCode.compile_detector_sampler()
    # one_sample = detector_sampler.sample(shots=1)[0]
    # for k in range(0, len(one_sample), DISTANCE-1):
    #     timeslice = one_sample[k:k+DISTANCE-1]
    #     print("".join("!" if e else "_" for e in timeslice))

    numLogicalErrors = countLogicalErrors(repetitionCode, SAMPLING_SHOTS)
    print(f"Number of logical errors: {numLogicalErrors}")

    errorModel = repetitionCode.detector_error_model(decompose_errors=True)
    #utils.saveSVG(errorModel, "matchgraph-svg", "pictures/01_repetition_code_matchgraph")

    #print(repetitionCode.diagram())
    utils.saveSVG(repetitionCode, "timeline-svg", "pictures/01_repetition_code_timeline")
    utils.saveSVG(repetitionCode, "timeslice-svg", "pictures/01_repetition_code_timeslice")