import uf_arch.uf_arch as uf
import stim
import numpy as np
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import utils

from error_models import SuperconductiveEM

SHOTS = 1000

MIN_DISTANCE = 5
MAX_DISTANCE = 31
DISTANCE_RANGE = range(MIN_DISTANCE, MAX_DISTANCE + 1, 2)

MIN_ERROR_RATE = 0.001
MAX_ERROR_RATE = 0.01
ERROR_RATE_STEP = 2
ERROR_RATE_RANGE = np.linspace(MIN_ERROR_RATE, MAX_ERROR_RATE, ERROR_RATE_STEP)

RESULTS_DIR = "results"
RESULTS_PATH = f"{RESULTS_DIR}/experiment_results.csv"

def sample_fromStim(stimSample, distance):
    period = (distance + 1) * ((distance - 1) // 2)

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

def execExperiment():
    experimentFrame = pd.DataFrame(columns=["repetition", "distance", "base_error_rate", "num_grow_merge_iters", "boundaries_per_iter", "odd_clusters_per_iter", "merges_per_iter"])

    for distance in DISTANCE_RANGE:
        for base_error_rate in ERROR_RATE_RANGE:
            error_count = 0

            print(f"Distance: {distance}, Base Error Rate: {base_error_rate}")

            errorModel = SuperconductiveEM(base_error_rate)
            stimErrorModel = errorModel.toStim()

            ufDecoder = uf.UnionFindDecoder(distance, distance+1, uf.CodeType.ROTATED, 1, 1)

            rotatedCode = stim.Circuit.generated(
                    "surface_code:rotated_memory_z",
                    rounds=distance,
                    distance=distance,
                    before_round_data_depolarization=stimErrorModel["before_round_data_depolarization"],
                    before_measure_flip_probability=stimErrorModel["before_measure_flip_probability"],
                    after_clifford_depolarization=stimErrorModel["after_clifford_depolarization"],
                    after_reset_flip_probability=stimErrorModel["after_reset_flip_probability"],
                )

            # utils.saveSVG(rotatedCode, "detslice-svg", f"pictures/experiment_detslice.svg")
            # utils.saveSVG(rotatedCode, "timeline-svg", f"pictures/experiment_timeline.svg")

            sampler = rotatedCode.compile_detector_sampler()
            samples, observables = sampler.sample(shots=SHOTS, separate_observables=True)

            dem = rotatedCode.detector_error_model()
            detCoords = dem.get_detector_coordinates()

            statsList = []

            for k, sample in enumerate(tqdm(samples)):
                sample = list(sample)

                roundLen = (distance + 1) * ((distance - 1) // 2)

                firstRound = sample[:roundLen]
                innerRounds = sample[roundLen:-roundLen]
                lastRound = sample[-roundLen:]

                innerOnlyZ = []

                for i, round in enumerate(innerRounds):
                    coord = detCoords[i+roundLen]
                    if (coord[0] // 2) % 2 == 0 and (coord[1] // 2) % 2 == 0 or (coord[0] // 2) % 2 == 1 and (coord[1] // 2) % 2 == 1:
                        innerOnlyZ.append(round)

                z_sample = firstRound + innerOnlyZ + lastRound
                z_sample = sample_fromStim(z_sample, distance)

                ufDecoder.decode(z_sample)
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

    plt.show()

if __name__ == "__main__":
    execExperiment()
    #plotExperimentResults()
