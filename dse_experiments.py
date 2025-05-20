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
RESULTS_PATH = f"{RESULTS_DIR}/experiment_results.csv"

def sample_fromStim(stimSample, distance):
    columnLength = (distance - 1) // 2
    period = (distance + 1) * columnLength

    starter_list = [0] * (distance - 1)
    for i in range((distance - 1) // 2):
        starter_list[2*i] = (distance - 1) - i - 1
    for i in range((distance - 1) // 2):
        starter_list[2*i + 1] = (distance - 1) // 2 - i - 1

    # for i in range(period // columnLength):
    #     stimSample[2*i], stimSample[2*i + 1] = stimSample[2*i + 1], stimSample[2*i]

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

    
    # offset = len(stimSample) - period
    # for i in range(period // columnLength):
    #     stimSample[offset + 2*i], stimSample[offset + 2*i + 1] = stimSample[offset + 2*i + 1], stimSample[offset + 2*i]

    return stimSample

def execExperiment():
    experimentFrame = pd.DataFrame(columns=["repetition", "distance", "base_error_rate", "num_grow_merge_iters", "boundaries_per_iter", "odd_clusters_per_iter", "merges_per_iter"])
    accuracyPrelimTest = pd.DataFrame(columns=["distance", "base_error_rate", "uf_arch_error_rate", "qsurf_deviation", "uf_arch_deviation", "test_total_deviation"])

    for distance in DISTANCE_RANGE:
        for base_error_rate in ERROR_RATE_RANGE:
            error_count = 0
            qSurfDeviation = 0
            invDeviation = 0

            TEST_totalDeviaton = 0

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

                rounds = distance + 1
                rowLen = (distance - 1) // 2
                columnLen = (distance + 1)
                roundLen = rowLen * columnLen

                firstRound = sample[:roundLen]
                innerRounds = sample[roundLen:-roundLen]
                lastRound = sample[-roundLen:]

                innerOnlyZ = []
                innerOnlyX = []

                for i, round in enumerate(innerRounds):
                    coord = detCoords[i+roundLen]
                    if (coord[0] // 2) % 2 == (coord[1] // 2) % 2:
                        innerOnlyZ.append(round)
                    else:
                        innerOnlyX.append(round)

                z_sample = firstRound + innerOnlyZ + lastRound

                dbg_triggerd = []

                input_sample = [0] * (roundLen * (distance + 1))
                for i_bit, bit in enumerate(sample):
                    coords = detCoords[i_bit]
                    if bit and (coords[0] // 2) % 2 == (coords[1] // 2) % 2:
                        dbg_triggerd.append(coords)
                        unrolledCoords = coords[2] * roundLen + (coords[1] // 2 - 1) * columnLen // 2 + coords[0] // 4
                        unrolledCoords = int(unrolledCoords)
                        input_sample[unrolledCoords] = 1

                input_sample = sample_fromStim(input_sample, distance)

                ufDecoder.decode(input_sample)
                stats = ufDecoder.get_stats()
                corrections = ufDecoder.get_horizontal_corrections()

                qSurfParity, qSurfCorrections, qSurfTriggered = utils.countLogicalErrors_uf_rotated_single_shot(dem, sample, observables[k])
                
                # parity means counting the number of corrections with coordinate [1] == 0
                parity = 0
                for correction in corrections:
                    if correction[2] == distance-1:
                        parity ^= 1

                if parity != observables[k]:
                    error_count += 1
                    if qSurfParity != parity:
                        qSurfDeviation += 1
                elif qSurfParity != parity:
                    invDeviation += 1

                if qSurfParity != parity:
                    TEST_totalDeviaton += 1

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
            print(f"QSurf is right, UFArch is wrong (d={distance}, error_rate={base_error_rate}): {qSurfDeviation / SHOTS}")
            print(f"UFArch is right, QSurf is wrong (d={distance}, error_rate={base_error_rate}): {invDeviation / SHOTS}")
            print(f"TEST Total Deviation(d={distance}, error_rate={base_error_rate}): {TEST_totalDeviaton / SHOTS}")
            #print(f"Theoretical Accuracy (d={distance}, error_rate={base_error_rate}): {1-error_rate+qSurfDeviation/SHOTS}")
            accuracyPrelimTest.loc[len(accuracyPrelimTest)] = {
                "distance": distance,
                "base_error_rate": base_error_rate,
                "uf_arch_error_rate": error_rate,
                "qsurf_deviation": qSurfDeviation / SHOTS,
                "uf_arch_deviation": invDeviation / SHOTS
            }

            # Save the experimentFrame to a CSV file
            experimentFrame.to_csv(RESULTS_PATH, index=False)
            accuracyPrelimTest.to_csv(f"{RESULTS_DIR}/accuracy_prelim_test.csv", index=False)

    # Final saving
    experimentFrame.to_csv(RESULTS_PATH, index=False)
    accuracyPrelimTest.to_csv(f"{RESULTS_DIR}/accuracy_prelim_test.csv", index=False)

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
