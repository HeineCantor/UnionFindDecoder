import uf_arch.uf_arch as uf
import stim
import numpy as np
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import utils

import pandas as pd
import matplotlib.pyplot as plt

from error_models import SuperconductiveEM

SHOTS = 1000

MIN_DISTANCE = 3
MAX_DISTANCE = 31
DISTANCE_RANGE = range(MIN_DISTANCE, MAX_DISTANCE + 1, 2)

MIN_ERROR_RATE = 0.001
MAX_ERROR_RATE = 0.01
ERROR_RATE_STEP = 10
ERROR_RATE_RANGE = np.linspace(MIN_ERROR_RATE, MAX_ERROR_RATE, ERROR_RATE_STEP)

RESULTS_DIR = "results"
RESULTS_PATH = f"{RESULTS_DIR}/dse_experiment_results.csv"

def fromStim(stimSample, dem, distance):
    rowLen = (distance - 1) // 2
    columnLen = (distance + 1)
    roundLen = rowLen * columnLen

    detCoords = dem.get_detector_coordinates()

    input_sample = [0] * (roundLen * (distance + 1))
    for i_bit, bit in enumerate(stimSample):
        coords = detCoords[i_bit]
        if bit and (coords[0] // 2) % 2 == (coords[1] // 2) % 2:
            unrolledCoords = coords[2] * roundLen + (coords[1] // 2 - 1) * columnLen // 2 + coords[0] // 4
            unrolledCoords = int(unrolledCoords)
            input_sample[unrolledCoords] = 1

    input_sample = rotate_fromStim(input_sample, distance)

    return input_sample

def rotate_fromStim(stimSample, distance):
    """
    This function takes an ordered syndrome and converts it to a rotated ordered syndrome.
    """
    columnLength = (distance - 1) // 2
    period = (distance + 1) * columnLength

    starter_list = [0] * (distance - 1)
    for i in range((distance - 1) // 2):
        starter_list[2*i] = (distance - 1) - i - 1
    for i in range((distance - 1) // 2):
        starter_list[2*i + 1] = (distance - 1) // 2 - i - 1

    for i in range(len(stimSample) // period):
        round = stimSample[i * period:(i + 1) * period]
        converted = [0] * period
        for j in range(len(round)):
            inner_period = 1 + (distance-1) // 2
            inner_sum = j % inner_period * (distance - 1)
            inner_offset = starter_list[j // inner_period]
            conv_coord = inner_offset + inner_sum
            converted[conv_coord] = round[j]
        stimSample[i * period:(i + 1) * period] = converted

    return stimSample

def execExperiment():
    experimentFrame = pd.DataFrame(columns=["repetition", "distance", "base_error_rate", "num_grow_merge_iters", "boundaries_per_iter", "odd_clusters_per_iter", "merges_per_iter", "num_peeling_iters"])

    for distance in DISTANCE_RANGE:
        for base_error_rate in ERROR_RATE_RANGE:
            error_count = 0

            errorModel = SuperconductiveEM(base_error_rate)
            stimErrorModel = errorModel.toStim()

            # rounds are distance + 1 because Stim always generates an additional final round
            ufDecoder = uf.UnionFindDecoder(distance, distance+1, uf.CodeType.ROTATED)

            rotatedCode = stim.Circuit.generated(
                    "surface_code:rotated_memory_z",
                    rounds=distance,
                    distance=distance,
                    before_round_data_depolarization=stimErrorModel["before_round_data_depolarization"],
                    before_measure_flip_probability=stimErrorModel["before_measure_flip_probability"],
                    after_clifford_depolarization=stimErrorModel["after_clifford_depolarization"],
                    after_reset_flip_probability=stimErrorModel["after_reset_flip_probability"],
                )

            sampler = rotatedCode.compile_detector_sampler()
            samples, observables = sampler.sample(shots=SHOTS, separate_observables=True)

            dem = rotatedCode.detector_error_model()

            for k, sample in enumerate(tqdm(samples)):
                sample = list(sample)

                input_sample = fromStim(sample, dem, distance)

                ufDecoder.decode(input_sample)
                stats = ufDecoder.get_stats()
                corrections = ufDecoder.get_horizontal_corrections()

                # parity means counting the number of corrections with coordinate [1] == 0
                parity = 0
                for correction in corrections:
                    if correction[2] == distance-1:
                        parity ^= 1

                if parity != observables[k]:
                    error_count += 1

                experimentFrame.loc[len(experimentFrame)] = {
                    "repetition": k,
                    "distance": distance,
                    "base_error_rate": base_error_rate,
                    "num_grow_merge_iters": stats.num_grow_merge_iters,
                    "boundaries_per_iter": stats.boundaries_per_iter,
                    "odd_clusters_per_iter": stats.odd_clusters_per_iter,
                    "merges_per_iter": stats.merges_per_iter,
                    "num_peeling_iters": stats.num_peeling_iters
                }

            # Calculate the error rate
            error_rate = error_count / SHOTS
            print(f"Accuracy (d={distance}, error_rate={base_error_rate}): {1-error_rate}")

            # Save the experimentFrame to a CSV file
            experimentFrame.to_csv(RESULTS_PATH, index=False)

    # Final saving
    experimentFrame.to_csv(RESULTS_PATH, index=False)

def plotExperimentResults():
    experimentFrame = pd.read_csv(RESULTS_PATH)

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        avgGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].mean()
        #maxGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].max()
        
        plt.plot(avgGrowMergeIters.index, avgGrowMergeIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Average number of Grow-Merge Iterations")
    plt.yticks(np.arange(0, 15, 2))
    plt.title(f"Average number of Grow-Merge Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        maxGrowMergeIters = aggregatedFrame.groupby("base_error_rate")["num_grow_merge_iters"].max()
        
        plt.plot(maxGrowMergeIters.index, maxGrowMergeIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Max number of Grow-Merge Iterations")
    plt.yticks(np.arange(0, 30, 2))
    plt.title(f"Max number of Grow-Merge Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["boundaries_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of boundaries per iteration")
    plt.title(f"Average number of boundaries per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["odd_clusters_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of odd clusters per iteration")
    plt.title(f"Average number of odd clusters per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        # Aggregate on repetitions
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        
        # get all the lists in the column "boundaries_per_iter" grouped by "base_error_rate"
        boundariesPerIter = aggregatedFrame.groupby("base_error_rate")["merges_per_iter"].apply(list)
        
        # for each base_error_rate, make all the internal lists the same size by padding with 0s
        for collection in boundariesPerIter:
            collection = [eval(element) for element in collection]
            maxLength = max(len(x) for x in collection)
            collection = [x + [0] * (maxLength - len(x)) for x in collection]
            collection = np.array(collection)
            avgBoundariesPerIter = np.mean(collection, axis=0)
            plt.plot(avgBoundariesPerIter, label=f"d={distance}")
            current_error_rate = boundariesPerIter.index[0]
            break

    plt.xlabel("Iteration")
    plt.ylabel("Average number of merges per iteration")
    plt.title(f"Average number of merges per iteration vs Base Error Rate at {current_error_rate} error rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()

    plt.figure()

    for distance in DISTANCE_RANGE:
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        peelingIters = aggregatedFrame.groupby("base_error_rate")["num_peeling_iters"].mean()
        plt.plot(peelingIters.index, peelingIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Average number of Peeling Iterations")
    plt.title(f"Average number of Peeling Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()
    plt.xticks(ERROR_RATE_RANGE)
    plt.yticks(np.arange(0, peelingIters.max()+5, 2))

    plt.figure()

    for distance in DISTANCE_RANGE:
        aggregatedFrame = experimentFrame[experimentFrame["distance"] == distance]
        peelingIters = aggregatedFrame.groupby("base_error_rate")["num_peeling_iters"].max()
        plt.plot(peelingIters.index, peelingIters.values, label=f"d={distance}")

    plt.xlabel("Base Error Rate")
    plt.ylabel("Max number of Peeling Iterations")
    plt.title(f"Max number of Peeling Iterations vs Base Error Rate ({SHOTS} shots)")
    plt.legend()
    plt.grid()
    plt.xticks(ERROR_RATE_RANGE)
    plt.yticks(np.arange(0, peelingIters.max()+5, 2))

    plt.show()

if __name__ == "__main__":
    #execExperiment()
    plotExperimentResults()
    #plotAccuracyValidationTest()