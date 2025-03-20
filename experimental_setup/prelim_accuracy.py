import stim, sinter
from typing import List
import numpy as np

from custom_decoders.unionfind.union_find_decoder import UnionFindDecoder
from error_models.superconductive_em import SuperconductiveEM
from error_models.only_measure_em import OnlyMeasureEM
from error_models.willow_em import WillowEM

START_DISTANCE = 3
END_DISTANCE = 31

START_ROUNDS = 25
END_ROUNDS = 100
ROUNDS_TESTS = 10

START_SHOTS = 10**3
END_SHOTS = 10**4
SHOTS_TESTS = 10

CONST_DISTANCE = 23
CONST_SHOTS = 10**4
CONST_ROUNDS = 100

CONST_SHOTS_FOR_VARIANCE = 10**3
CONST_VARIANCE_COUNT = 50

DISTANCE_RANGE = range(END_DISTANCE, START_DISTANCE, -2)
SHOTS_RANGE = np.linspace(START_SHOTS, END_SHOTS, SHOTS_TESTS, dtype=int).tolist()[::-1]
ROUNDS_RANGE = np.linspace(START_ROUNDS, END_ROUNDS, ROUNDS_TESTS, dtype=int).tolist()[::-1]

MAX_ERRORS = CONST_SHOTS // 20

CORES = 14

#noiseModel = SuperconductiveEM(0.003) # 0.3% base noise (Sycamore-approximated)
noiseModel = WillowEM() # Willow noise model

def execExperiment(distanceList, shotsList, roundsList, codeType, decoder):
    collected_stats = None

    for shots in shotsList:
        for rounds in roundsList:
            customDecodersDict = None
            if decoder == "union_find_decoder":
                customDecodersDict = {"union_find_decoder": UnionFindDecoder(codeType)}

            task = [
                sinter.Task(
                    circuit=stim.Circuit.generated(
                        codeType,
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
                    decoders=[decoder],
                    custom_decoders=customDecodersDict,
                    print_progress=True
                )

            if collected_stats is None:
                collected_stats: List[sinter.TaskStats] = sinterCollection
            else:
                collected_stats += sinterCollection

    return collected_stats

def accuracyByDistance(codeType, decoder):
    retStats = []
    for distance in DISTANCE_RANGE:
        retStats.append(execExperiment([distance], [CONST_SHOTS], [CONST_ROUNDS], codeType, decoder))
    return retStats

def accuracyByShots(codeType, decoder):
    return execExperiment([CONST_DISTANCE], SHOTS_RANGE, [CONST_ROUNDS], codeType, decoder)

def accuracyByRounds(codeType, decoder):
    return execExperiment([CONST_DISTANCE], [CONST_SHOTS], ROUNDS_RANGE, codeType, decoder)

def accuracyVariance(codeType, decoder):
    repetitionStats = []

    for _ in range(CONST_VARIANCE_COUNT):
        result = execExperiment([CONST_DISTANCE], [CONST_SHOTS_FOR_VARIANCE], [CONST_ROUNDS], codeType, decoder)
        repetitionStats.append(result)

    return repetitionStats