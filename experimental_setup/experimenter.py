import stim, sinter
from typing import List

from custom_decoders.unionfind.union_find_decoder import UnionFindDecoder
from error_models import ErrorModel, SuperconductiveEM, WillowEM

noiseModelDict = {
    "si1000_004": SuperconductiveEM(0.004),
    "willow": WillowEM()
}

codeTypeDict = {
    "repetition": "repetition_code:memory",
    "unrotated": "surface_code:unrotated_memory_z",
    "rotated": "surface_code:rotated_memory_z",
}

decoderDict = {
    "sparse_blossom": "pymatching",
    "union_find": "union_find_decoder"
}

CORES = 14

class Experimenter():
    def execExperiment(distanceList, shotsList, roundsList, codeType, decoder, noiseModel):
        collected_stats = None

        noiseModel = noiseModelDict[noiseModel]
        codeType = codeTypeDict[codeType]
        decoder = decoderDict[decoder]

        shotsList = [int(shots) for shots in shotsList]

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

        error_rate = collected_stats[0].errors / collected_stats[0].shots
        runtime = collected_stats[0].seconds

        return error_rate, runtime