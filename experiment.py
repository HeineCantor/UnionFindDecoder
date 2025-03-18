import matplotlib.pyplot as plt

import experimental_setup.prelim_accuracy as prelim_accuracy
from experimental_setup.plotter import plotAccuracyByDistance, plotAccuracyByShots, plotAccuracyByRounds, plotAccuracyByVariance, plotDistributionVariance

CODE_TYPE = "surface_code:rotated_memory_z"
DECODER = "pymatching"

def testAndSaveDistance():
    stats_distance = prelim_accuracy.accuracyByDistance()
    with open("results_distance.txt", "w") as f:
        f.write(str(stats_distance).replace('),','),\n'))

def testAndSaveShots():
    stats_shots = prelim_accuracy.accuracyByShots()
    with open("results_shots.txt", "w") as f:
        f.write(str(stats_shots).replace('),','),\n'))

def testAndSaveRounds():
    stats_rounds = prelim_accuracy.accuracyByRounds()
    with open("results_rounds.txt", "w") as f:
        f.write(str(stats_rounds).replace('),','),\n'))

def testAndSaveVariance():
    stats_variance = prelim_accuracy.accuracyVariance()
    with open("results_variance.txt", "w") as f:
        f.write(str(stats_variance).replace('),','),\n'))

if __name__ == "__main__":
    testAndSaveDistance()
    testAndSaveShots()
    testAndSaveRounds()
    testAndSaveVariance()

    plotAccuracyByDistance()
    plotAccuracyByShots()
    plotAccuracyByRounds()
    plotAccuracyByVariance()
    plotDistributionVariance()

    plt.show()