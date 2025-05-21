import sinter
import stim
import numpy as np
import pathlib
import math

import uf_arch.uf_arch as uf

class UFArchDecoder(sinter.Decoder):
    def __init__(self, codeType: str):
        super().__init__()
        self.codeType = codeType

    def decode_via_files(self,
                         *,
                         num_shots: int,
                         num_dets: int,
                         num_obs: int,
                         dem_path: pathlib.Path,
                         dets_b8_in_path: pathlib.Path,
                         obs_predictions_b8_out_path: pathlib.Path,
                         tmp_dir: pathlib.Path,
                       ) -> None:
        
        detCoords = stim.DetectorErrorModel.from_file(dem_path).get_detector_coordinates()
        distance, rounds = getCodeParams(detCoords, self.codeType)

        ufDecoder = uf.UnionFindDecoder(distance, distance+1, uf.CodeType.ROTATED, 1, 1)

        packed_detection_event_data = np.fromfile(dets_b8_in_path, dtype=np.uint8)
        packed_detection_event_data.shape = (num_shots, math.ceil(num_dets / 8))

        # Make predictions.
        all_predictions = []
        for shot in packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            
            # TODO: extract method
            rowLen = (distance - 1) // 2
            columnLen = (distance + 1)
            roundLen = rowLen * columnLen

            dbg_triggerd = []

            input_sample = [0] * (roundLen * (distance + 1))
            for i_bit, bit in enumerate(unpacked):
                coords = detCoords[i_bit]
                if bit and (coords[0] // 2) % 2 == (coords[1] // 2) % 2:
                    dbg_triggerd.append(coords)
                    unrolledCoords = coords[2] * roundLen + (coords[1] // 2 - 1) * columnLen // 2 + coords[0] // 4
                    unrolledCoords = int(unrolledCoords)
                    input_sample[unrolledCoords] = 1

            input_sample = sample_fromStim(input_sample, distance)

            try:
                ufDecoder.decode(input_sample)
                stats = ufDecoder.get_stats()
                corrections = ufDecoder.get_horizontal_corrections()

                # parity means counting the number of corrections with coordinate [1] == 0
                parity = 0
                for correction in corrections:
                    if correction[2] == distance-1:
                        parity ^= 1
            except:
                parity = 0

            prediction = [parity]

            all_predictions.append(prediction)

        # Write predictions.
        np.packbits(all_predictions, axis=1, bitorder='little').tofile(obs_predictions_b8_out_path)

def sample_fromStim(stimSample, distance):
    columnLength = (distance - 1) // 2
    period = (distance + 1) * columnLength

    starter_list = [0] * (distance - 1)
    for i in range((distance - 1) // 2):
        starter_list[2*i] = (distance - 1) - i - 1
    for i in range((distance - 1) // 2):
        starter_list[2*i + 1] = (distance - 1) // 2 - i - 1

    for i in range(len(stimSample) // period):
        round = stimSample[i * period:(i + 1) * period]
        #converted = [round[2], round[0], round[3], round[1]]
        converted = [0] * period
        for j in range(len(round)):
            inner_period = 1 + (distance-1) // 2
            inner_sum = j % inner_period * (distance - 1)
            inner_offset = starter_list[j // inner_period]
            conv_coord = inner_offset + inner_sum
            converted[conv_coord] = round[j]
        stimSample[i * period:(i + 1) * period] = converted

    return stimSample

def getCodeParams(detCoords: dict, codeType: str) -> dict:
    distance = 0

    if True or codeType == "rotated":
        distance = getRotatedParams(detCoords)
    elif codeType == "planar":
        distance = getUnrotatedParams(detCoords)
    elif codeType == "repetition":
        distance = getRepetitionParams(detCoords)

    rounds = int(list(detCoords.values())[-1][-1])

    return distance, rounds

def getRotatedParams(detCoords: dict) -> dict:
    distance = int(list(detCoords.values())[-1][0] / 2) # the last coordinate is the one with the highest x value, so take it and halve it

    return distance

def getUnrotatedParams(detCoords: dict) -> dict:
    distance = int(list(detCoords.values())[-1][0] / 2) + 1

    return distance

def getRepetitionParams(detCoords: dict) -> dict:
    distance = int(list(detCoords.values())[-1][0]+1) // 2 + 1

    return distance
