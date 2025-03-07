import math
import pathlib
import numpy as np
import sinter
import stim

class UnionFindDecoder(sinter.Decoder):
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


        self.init_from_dem(stim.DetectorErrorModel.from_file(dem_path))

        packed_detection_event_data = np.fromfile(dets_b8_in_path, dtype=np.uint8)
        packed_detection_event_data.shape = (num_shots, math.ceil(num_dets / 8))

        # Make predictions.
        all_predictions = []
        for shot in packed_detection_event_data:
            unpacked = np.unpackbits(shot, bitorder='little')
            prediction = self.predict_from_dem(sample=unpacked)
            all_predictions.append(prediction)

        # Write predictions.
        np.packbits(all_predictions, axis=1, bitorder='little').tofile(obs_predictions_b8_out_path)

    def compile_decoder_for_dem(self, *, dem: stim.DetectorErrorModel) -> 'sinter.CompiledDecoder':
        # This will be added in v1.12 and sinter will prefer it, as it avoids the disk as a bottleneck.
        #
        # You have to return an object with this method:
        #    def decode_shots_bit_packed(
        #                self,
        #                *,
        #                bit_packed_detection_event_data: np.ndarray,
        #        ) -> np.ndarray:
        raise NotImplementedError()
    
    def init_from_dem(self, dem: stim.DetectorErrorModel) -> None:
        self.detCoords = dem.get_detector_coordinates()

        # Note: approximation. We should actually the max of all three dimensions.
        self.distance = int(list(self.detCoords.values())[-1][-1])

        self.convCoords = {}

        if self.CODE_TYPES[self.codeType] == "rotated":
            for i in range(len(self.detCoords)):
                self.convCoords[i] = (self.detCoords[i][0] / 2 - 0.5, self.detCoords[i][1] / 2 - 0.5, self.detCoords[i][2])
        elif self.CODE_TYPES[self.codeType] == "planar":
            for i in range(len(self.detCoords)):
                self.convCoords[i] = (self.detCoords[i][0] / 2 + 0.5, self.detCoords[i][1] / 2, self.detCoords[i][2])

    def predict_from_dem(self, sample: np.ndarray) -> np.ndarray:
        try:
            from qsurface.main import initialize, run
        except Exception as e:
            if e is ImportError:
                raise ImportError("You need to install the qsurface package to use this decoder.") 
            else:
                raise e

        code, decoder = initialize((self.distance, self.distance), self.CODE_TYPES[self.codeType], "unionfind", enabled_errors=["pauli"], faulty_measurements=True, initial_states=(0,0))

        error_dict_for_qsurface = {}
        for i, err in enumerate(sample):
            if err == 1:
                error_dict_for_qsurface[self.convCoords[i]] = err

        # Note: error rates are useless.
        output = run(code, decoder, error_rates = {"p_bitflip": 0.1, "p_phaseflip": 0.1}, decode_initial=False, custom_error_dict=error_dict_for_qsurface)
        matchings = output["matchings"]

        # Conversion from qSurface matching notation.
        # Note: should be generalized. We must take only the memory measurement observables (z or x) and the convertion 
        #       should be done with respect to the code type.
        if self.CODE_TYPES[self.codeType] == "rotated":
            matchings = [str(m[0]).removeprefix("ex-").removeprefix("ex|").split('|')[0] for m in matchings if "ex" in str(m[0])]
            matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
            matchings = [(int((m[0] + 0.5) * 2), int((m[1] + 0.5) * 2)) for m in matchings]
        elif self.CODE_TYPES[self.codeType] == "planar":
            matchings = [str(m[0]).removeprefix("ez-").removeprefix("ez|").split('|')[0] for m in matchings if "ez" in str(m[0])]
            matchings = [(float(m.split(',')[0][1:]), float(m.split(',')[1][:-1])) for m in matchings]
            matchings = [(int((m[0] - 0.5) * 2), int(m[1] * 2)) for m in matchings]

        tmpParity = 0

        obsYCoord = self.OBSERVABLE_Y_COORD[self.CODE_TYPES[self.codeType]]

        for m in matchings:
            if m[1] == obsYCoord:
                tmpParity ^= 1

        return [tmpParity]