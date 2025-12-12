import stim, sinter
from typing import List
import pandas as pd

from experimental_setup import config
from custom_decoders.unionfind.union_find_decoder import UnionFindDecoder
from custom_decoders.uf_arch.uf_arch_decoder import UFArchDecoder, UFArchParams
from error_models import ErrorModel, SuperconductiveEM, WillowEM

noiseModelDict = {
    "si1000": SuperconductiveEM,
    "willow": WillowEM
}

codeTypeDict = {
    "repetition": "repetition_code:memory",
    "unrotated": "surface_code:unrotated_memory_z",
    "rotated": "surface_code:rotated_memory_z",
}

decoderDict = {
    "sparse_blossom": "pymatching",
    "union_find": "union_find",
    "uf_arch": "uf_arch"
}

CORES = 16

class Experimenter():
    def execExperiment(distanceList, shotsList, roundsList, errorRate, codeType, decoder, noiseModel : ErrorModel, **kwargs):
        collected_stats = None

        noiseModel = noiseModelDict[noiseModel](errorRate)
        codeType = codeTypeDict[codeType]
        decoder = decoderDict[decoder]

        shotsList = [int(shots) for shots in shotsList]

        stimNoiseModel = noiseModel.toStim()
        
        early_stopping_param = -1
        early_stopping_peeling_param = -1
        if "early_stopping_param" in kwargs:
            early_stopping_param = kwargs["early_stopping_param"]
            if early_stopping_param is None:
                early_stopping_param = -1
        if "early_stopping_peeling_param" in kwargs:
            early_stopping_peeling_param = kwargs["early_stopping_peeling_param"]
            if early_stopping_peeling_param is None:
                early_stopping_peeling_param = -1

        params = UFArchParams(codeType=codeType)
        params.early_stopping_param = early_stopping_param
        params.early_stopping_peeling_param = early_stopping_peeling_param
        
        for shots in shotsList:
            for rounds in roundsList:
                customDecodersDict = {
                    config.UNION_FIND_DECODER: UnionFindDecoder(codeType), 
                    config.UF_ARCH_DECODER: UFArchDecoder(params=params)
                }

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
                        json_metadata={'d': d, 'r': rounds, 'error_model': noiseModel.name, 'base_error_rate': errorRate},
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
    
    def execExperimentFromRow(row : pd.Series, **kwargs):
        return Experimenter.execExperiment(
            [row["distance"]],
            [row["shots"]],
            [row["rounds"]],
            row["base_error_rate"],
            row["code"],
            row["decoder"],
            row["noiseModel"],
            **kwargs
        )