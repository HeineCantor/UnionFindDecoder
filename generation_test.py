import stim

import utils
import time

DISTANCE = 3
dataFlipNoise = 0.01
measFlipNoise = 0.01

SAMPLES = DISTANCE
SHOTS = 1000

if __name__ == "__main__":
    surfaceCode = stim.Circuit.generated(
        "surface_code:unrotated_memory_z",
        rounds=DISTANCE-1,
        distance=DISTANCE,
        before_round_data_depolarization=dataFlipNoise,
        before_measure_flip_probability=measFlipNoise
    ) 

    dem = surfaceCode.detector_error_model()

    utils.saveSVG(surfaceCode, "detslice-svg", "pictures/generation_test_detslice.svg")
    utils.saveSVG(surfaceCode, "timeline-svg", "pictures/generation_test_timeline.svg")

    detectorSampler = surfaceCode.compile_detector_sampler()

    start = time.time()
    samples = detectorSampler.sample(shots=SHOTS)
    end = time.time()

    print(f"Sampling took {end - start} seconds. Rate: {(end - start) / SHOTS} s/shot")

    # for i, sample in enumerate(samples):
    #     print(f"[{i}] Sample ({len(sample)}): {[int(x) for x in sample]}")