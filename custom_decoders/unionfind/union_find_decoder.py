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
}

OBSERVABLE_Y_COORD = {
    "rotated" : 1,
    "planar" : 0
}

OBSERVABLE_DATA_POSITION = {
    "rotated" : 1,
    "planar" : 0
}

class UnionFindCompiledDecoder(sinter.CompiledDecoder):
    def __init__(self, codeType : str, detector_error_model : stim.DetectorErrorModel, rounds : int = None):
        super().__init__()
        self.codeType = codeType
        self.dem = detector_error_model
        self.convCoords = init_from_dem(detector_error_model, codeType)
        self.rounds = rounds

    def decode_shots_bit_packed(self, *, bit_packed_detection_event_data: np.ndarray,) -> np.ndarray:
        all_predictions = []
        
        for shot in bit_packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            prediction = predict_from_dem(sample=unpacked, codeType=self.codeType, dem=self.dem, convCoords=self.convCoords, rounds=self.rounds)
            all_predictions.append(prediction)

        return np.packbits(all_predictions, axis=1, bitorder='little')
    
class UnionFindDecoder(sinter.Decoder):
    def __init__(self, codeType : str, rounds : int = None):
        super().__init__()
        self.codeType = codeType
        self.rounds = rounds

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

        self.convCoords, self.distance = init_from_dem(stim.DetectorErrorModel.from_file(dem_path), self.codeType)

        packed_detection_event_data = np.fromfile(dets_b8_in_path, dtype=np.uint8)
        packed_detection_event_data.shape = (num_shots, math.ceil(num_dets / 8))

        # Make predictions.
        all_predictions = []
        for shot in packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            prediction = predict_from_dem(sample=unpacked, rounds=self.rounds)
            all_predictions.append(prediction)

        # Write predictions.
        np.packbits(all_predictions, axis=1, bitorder='little').tofile(obs_predictions_b8_out_path)

    def compile_decoder_for_dem(self, *, dem: stim.DetectorErrorModel) -> 'sinter.CompiledDecoder':
        return UnionFindCompiledDecoder(self.codeType, dem, self.rounds)
    

def init_from_dem(dem: stim.DetectorErrorModel, codeType: str) -> dict:
    detCoords = dem.get_detector_coordinates()
    convCoords = {}

    #  TODO: estrai metodi + astrazione con classe
    if CODE_TYPES[codeType] == "rotated":
        for i in range(len(detCoords)):
            convCoords[i] = (detCoords[i][0] / 2 - 0.5, detCoords[i][1] / 2 - 0.5, detCoords[i][2])
    elif CODE_TYPES[codeType] == "planar":
        for i in range(len(detCoords)):
            convCoords[i] = (detCoords[i][0] / 2 + 0.5, detCoords[i][1] / 2, detCoords[i][2])

    return convCoords

def predict_from_dem(sample: np.ndarray, codeType : str, dem : stim.DetectorErrorModel, convCoords : dict, rounds : int = None) -> np.ndarray:
    try:
        from qsurface.main import initialize, run
    except Exception as e:
        if e is ImportError:
            raise ImportError("You need to install the qsurface package to use this decoder.") 
        else:
            raise e

    detCoords = dem.get_detector_coordinates()

    distance = int(list(detCoords.values())[-1][0] / 2)
    rounds = int(list(detCoords.values())[-1][-1])

    size = (distance, distance, distance+1)

    if rounds is not None:
        size = (distance, distance, rounds+1)

    code, decoder = initialize(size, CODE_TYPES[codeType], "unionfind", enabled_errors=["pauli"], plotting=False, faulty_measurements=True, initial_states=(0,0))

    error_dict_for_qsurface = {}
    for i, err in enumerate(sample):
        if err == 1:
            error_dict_for_qsurface[convCoords[i]] = err

    # Note: error rates are useless.
    output = run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)
    matchings = output["matchings"]

    # Conversion from qSurface matching notation.
    # Note: should be generalized. We must take only the memory measurement observables (z or x) and the convertion 
    #       should be done with respect to the code type.
    if CODE_TYPES[codeType] == "rotated":
        matchings = [str(m[0]).removeprefix("ex-").removeprefix("ex|").split('|')[0] for m in matchings if "ex" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] + 0.5) * 2), int((m[1] + 0.5) * 2)) for m in matchings]
    elif CODE_TYPES[codeType] == "planar":
        matchings = [str(m[0]).removeprefix("ez-").removeprefix("ez|").split('|')[0] for m in matchings if "ez" in str(m[0])]
        matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
        matchings = [(int((m[0] - 0.5) * 2), int(m[1] * 2)) for m in matchings]

    tmpParity = 0

    obsYCoord = OBSERVABLE_Y_COORD[CODE_TYPES[codeType]]
    obsDataPos = OBSERVABLE_DATA_POSITION[CODE_TYPES[codeType]]

    for m in matchings:
        if m[1] == obsYCoord and m[0] % 2 == obsDataPos:
            tmpParity ^= 1

    return [tmpParity]