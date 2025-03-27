import stim, sinter
from typing import List
import pandas as pd

from experimental_setup import config
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
    def execExperiment(distanceList, shotsList, roundsList, codeType, decoder, noiseModel : ErrorModel):
        collected_stats = None

        noiseModel = noiseModelDict[noiseModel]
        codeType = codeTypeDict[codeType]
        decoder = decoderDict[decoder]

        shotsList = [int(shots) for shots in shotsList]

        stimNoiseModel = noiseModel.toStim()

        for shots in shotsList:
            for rounds in roundsList:
                customDecodersDict = None
                if decoder == config.UNION_FIND_DECODER:
                    customDecodersDict = {config.UNION_FIND_DECODER: UnionFindDecoder(codeType)}

                rounds = int(rounds)
                task = [
                    sinter.Task(
                        circuit=stim.Circuit.generated(
                            codeType,
                            rounds=rounds,
                            distance=d,
                            before_round_data_depolarization=stimNoiseModel["before_round_data_depolarization"],
                            before_measure_flip_probability=stimNoiseModel["before_measure_flip_probability"],
                            after_clifford_depolarization=stimNoiseModel["after_clifford_depolarization"],
                            after_reset_flip_probability=stimNoiseModel["after_reset_flip_probability"],
                        ),
                        json_metadata={'d': d, 'r': rounds, 'error_model': noiseModel.name},
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
    
    def execExperimentFromRow(row : pd.Series):
        return Experimenter.execExperiment(
            [row["distance"]],
            [row["shots"]],
            [row["rounds"]],
            row["code"],
            row["decoder"],
            row["noiseModel"]
        )