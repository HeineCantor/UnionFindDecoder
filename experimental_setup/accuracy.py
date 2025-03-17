import stim, sinter
from typing import List
import numpy as np

from custom_decoders import unionfind
from error_models.superconductive_em import SuperconductiveEM
from error_models.only_measure_em import OnlyMeasureEM

START_DISTANCE = 3
END_DISTANCE = 37

START_ROUNDS = 25
END_ROUNDS = 600
ROUNDS_TESTS = 10

START_SHOTS = 10**4
END_SHOTS = 10**5
SHOTS_TESTS = 10

CONST_DISTANCE = 25
CONST_SHOTS = 10**4
CONST_ROUNDS = 100

CONST_VARIANCE_COUNT = 100

DISTANCE_RANGE = range(START_DISTANCE, END_DISTANCE + 1, 2)
SHOTS_RANGE = np.linspace(START_SHOTS, END_SHOTS, SHOTS_TESTS, dtype=int).tolist()
ROUNDS_RANGE = np.linspace(START_ROUNDS, END_ROUNDS, ROUNDS_TESTS, dtype=int).tolist()

MAX_ERRORS = CONST_SHOTS // 20

CORES = 14

CODE_TYPE = "surface_code:rotated_memory_z"
DECODER = "pymatching"

noiseModel = SuperconductiveEM(0.004) # 0.5% base noise

def execExperiment(distanceList, shotsList, roundsList):
    collected_stats = None

    for shots in shotsList:
        for rounds in roundsList:
            task = [
                sinter.Task(
                    circuit=stim.Circuit.generated(
                        CODE_TYPE,
                        rounds=rounds,
                        distance=d,
                        before_round_data_depolarization=noiseModel.getBeforeRoundDataDepolarizationErrorRate(),
                        before_measure_flip_probability=noiseModel.getBeforeMeasurementErrorRate(),
                        after_clifford_depolarization=noiseModel.getCliffordErrorRate(),
                        after_reset_flip_probability=noiseModel.getAfterResetErrorRate(),
                    ),
                    json_metadata={'d': d, 'p': noiseModel.error_rate, 'r': rounds, 'error_model': noiseModel.name},
                )
                for d in distanceList
            ]

            sinterCollection = sinter.collect(
                    num_workers=CORES,
                    tasks=task,
                    max_shots=shots,
                    max_errors=shots,
                    decoders=[DECODER],
                    print_progress=True
                )

            if collected_stats is None:
                collected_stats: List[sinter.TaskStats] = sinterCollection
            else:
                collected_stats += sinterCollection

    return collected_stats

def accuracyByDistance():
    return execExperiment(DISTANCE_RANGE, [CONST_SHOTS], [CONST_ROUNDS])

def accuracyByShots():
    return execExperiment([CONST_DISTANCE], SHOTS_RANGE, [CONST_ROUNDS])

def accuracyByRounds():
    return execExperiment([CONST_DISTANCE], [CONST_SHOTS], ROUNDS_RANGE)

def accuracyVariance():
    repetitionStats = []

    for _ in range(CONST_VARIANCE_COUNT):
        result = execExperiment([CONST_DISTANCE], [CONST_SHOTS], [CONST_ROUNDS])
        repetitionStats.append(result)

    return repetitionStats