import math
import pathlib
import numpy as np
import sinter
import stim

CODE_TYPES = {
    "surface_code:unrotated_memory_z" : "planar", # these are qsurface names
    "surface_code:rotated_memory_z" : "rotated",
    "surface_code:unrotated_memory_x" : "planar",
    "surface_code:rotated_memory_x" : "rotated",
    "repetition_code:memory" : "repetition"
}

OBSERVABLE_Y_COORD = {
    "rotated" : 1,
    "planar" : 0,
    "repetition" : 0
}

OBSERVABLE_DATA_POSITION = {
    "rotated" : 1,
    "planar" : 0,
    "repetition" : -1
}

class UnionFindCompiledDecoder(sinter.CompiledDecoder):
    def __init__(self, codeType : str, detector_error_model : stim.DetectorErrorModel):
        super().__init__()
        self.codeType = codeType
        self.dem = detector_error_model

        detCoords = detector_error_model.get_detector_coordinates()
        self.convCoords, self.distance, self.rounds = getCodeParams(detCoords, codeType)

    def decode_shots_bit_packed(self, *, bit_packed_detection_event_data: np.ndarray,) -> np.ndarray:
        all_predictions = []
        
        for shot in bit_packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            prediction = predict_from_qsurface(
                sample=unpacked, 
                codeType=self.codeType, 
                convCoords=self.convCoords, 
                distance=self.distance,
                rounds=self.rounds)
            all_predictions.append(prediction)

        return np.packbits(all_predictions, axis=1, bitorder='little')
    
class UnionFindDecoder(sinter.Decoder):
    def __init__(self, codeType : str):
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
        convCoords, distance, rounds = getCodeParams(detCoords, self.codeType)

        packed_detection_event_data = np.fromfile(dets_b8_in_path, dtype=np.uint8)
        packed_detection_event_data.shape = (num_shots, math.ceil(num_dets / 8))

        # Make predictions.
        all_predictions = []
        for shot in packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            prediction = predict_from_qsurface(
                sample=unpacked,
                codeType=self.codeType,
                convCoords=convCoords,
                distance=distance,
                rounds=rounds)
            all_predictions.append(prediction)

        # Write predictions.
        np.packbits(all_predictions, axis=1, bitorder='little').tofile(obs_predictions_b8_out_path)

    def compile_decoder_for_dem(self, *, dem: stim.DetectorErrorModel) -> 'sinter.CompiledDecoder':
        return UnionFindCompiledDecoder(self.codeType, dem)

def predict_from_qsurface(sample: np.ndarray, codeType : str, convCoords : dict, distance: int, rounds: int) -> np.ndarray:
    try:
        from qsurface.main import initialize, run
    except Exception as e:
        if e is ImportError:
            raise ImportError("You need to install the qsurface package to use this decoder.") 
        else:
            raise e

    # Initialize params for qsurface
    size = (distance, distance, rounds+1) # last round is to check final clifford errors
    error_dict_for_qsurface = getqSurfaceErrorDict(sample, convCoords)

    # Run decoder with params
    code, decoder = initialize(size, CODE_TYPES[codeType], "unionfind", enabled_errors=["pauli"], plotting=False, faulty_measurements=True, initial_states=(0,0))
    output = run(code, decoder, error_rates = {"p_bitflip": 0, "p_phaseflip": 0}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)

    # Get output matchings
    matchings = output["matchings"]

    # Get observable parity
    obsParity = getObservableParity(codeType, matchings, distance)

    return obsParity

def getCodeParams(detCoords: dict, codeType: str) -> dict:
    convCoords = {}
    distance = 0

    if CODE_TYPES[codeType] == "rotated":
        convCoords, distance = getRotatedParams(detCoords)
    elif CODE_TYPES[codeType] == "planar":
        convCoords, distance = getUnrotatedParams(detCoords)
    elif CODE_TYPES[codeType] == "repetition":
        convCoords, distance = getRepetitionParams(detCoords)

    rounds = int(list(detCoords.values())[-1][-1])

    return convCoords, distance, rounds

def getRotatedParams(detCoords: dict) -> dict:
    convCoords =  {i : (detCoords[i][0] / 2 - 0.5, detCoords[i][1] / 2 - 0.5, detCoords[i][2]) for i in range(len(detCoords))}
    distance = int(list(detCoords.values())[-1][0] / 2) # the last coordinate is the one with the highest x value, so take it and halve it

    return convCoords, distance

def getUnrotatedParams(detCoords: dict) -> dict:
    convCoords = {i : (detCoords[i][0] / 2 + 0.5, detCoords[i][1] / 2, detCoords[i][2]) for i in range(len(detCoords))}
    distance = int(list(detCoords.values())[-1][0] / 2) + 1

    return convCoords, distance

def getRepetitionParams(detCoords: dict) -> dict:
    convCoords = {i : (detCoords[i][0] / 2, 0, detCoords[i][1]) for i in range(len(detCoords))}
    distance = int(list(detCoords.values())[-1][0]+1) // 2 + 1

    return convCoords, distance

def getqSurfaceErrorDict(sample : np.ndarray, convCoords : dict) -> dict:
    error_dict_for_qsurface = {}
    for i, err in enumerate(sample):
        if err == 1:
            error_dict_for_qsurface[convCoords[i]] = err

    return error_dict_for_qsurface

# TODO: this is correct but could be optimized. Also, the observable exact coordinates should be taken from DEM (someway)
def getObservableParity(codeType : str, matchings : list, distance : int) -> np.ndarray:
    if CODE_TYPES[codeType] == "rotated":
        matchings = [str(m[0]).removeprefix("ex-").split('|')[0] for m in matchings if "ex-" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] + 0.5) * 2), int((m[1] + 0.5) * 2)) for m in matchings]
    elif CODE_TYPES[codeType] == "planar":
        matchings = [str(m[0]).removeprefix("ez-").split('|')[0] for m in matchings if "ez-" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] - 0.5) * 2), int(m[1] * 2)) for m in matchings]
    elif CODE_TYPES[codeType] == "repetition":
        matchings = [str(m[0]).removeprefix("ex-").split('|')[0] for m in matchings if "ex-" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int(m[0] * 2), 0) for m in matchings]

    tmpParity = 0

    obsYCoord = OBSERVABLE_Y_COORD[CODE_TYPES[codeType]]
    obsDataPos = OBSERVABLE_DATA_POSITION[CODE_TYPES[codeType]]

    if not CODE_TYPES[codeType] == "repetition":
        for m in matchings:
            if m[1] == obsYCoord and m[0] % 2 == obsDataPos:
                tmpParity ^= 1
    else:
        for m in matchings:
            if m[0] == (distance-1)*2:
                tmpParity ^= 1

    return [tmpParity]