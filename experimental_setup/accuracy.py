import stim, sinter
from typing import List

from custom_decoders import unionfind
from error_models.superconductive_em import SuperconductiveEM

START_DISTANCE = 3
END_DISTANCE = 15

CONST_DISTANCE = 11
CONST_SHOTS = 10**5
CONST_ROUNDS = 100

DISTANCE_RANGE = range(START_DISTANCE, END_DISTANCE + 1, 2)
SHOTS_RANGE = [10**i for i in range(4, 7)]
ROUNDS_RANGE = [10**i for i in range(2, 5)]

MAX_ERRORS = CONST_SHOTS // 20

CORES = 7

CODE_TYPE = "surface_code:rotated_memory_z"
DECODER = "pymatching"

noiseModel = SuperconductiveEM(0.01) # 1% base noise

def execExperiment(distanceList, shotsList, roundsList):
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
                    json_metadata={'d': d},
                )
                for d in distanceList
            ]

            collected_stats: List[sinter.TaskStats] = sinter.collect(
                num_workers=CORES,
                tasks=task,
                max_shots=shots,
                max_errors=MAX_ERRORS,
                decoders=[DECODER],
                print_progress=True
            )

            return collected_stats

def accuracyByDistance():
    return execExperiment(DISTANCE_RANGE, [CONST_SHOTS], [CONST_ROUNDS])