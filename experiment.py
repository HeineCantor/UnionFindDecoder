import matplotlib.pyplot as plt

import experimental_setup.accuracy as accuracy
from experimental_setup.plot_experiments import plotAccuracyByDistance, plotAccuracyByShots, plotAccuracyByRounds, plotAccuracyByVariance

def testAndSaveDistance():
    stats_distance = accuracy.accuracyByDistance()
    with open("results_distance.txt", "w") as f:
        f.write(str(stats_distance).replace('),','),\n'))

def testAndSaveShots():
    stats_shots = accuracy.accuracyByShots()
    with open("results_shots.txt", "w") as f:
        f.write(str(stats_shots).replace('),','),\n'))

def testAndSaveRounds():
    stats_rounds = accuracy.accuracyByRounds()
    with open("results_rounds.txt", "w") as f:
        f.write(str(stats_rounds).replace('),','),\n'))

def testAndSaveVariance():
    stats_variance = accuracy.accuracyVariance()
    with open("results_variance.txt", "w") as f:
        f.write(str(stats_variance).replace('),','),\n'))

if __name__ == "__main__":
    #testAndSaveDistance()
    #testAndSaveShots()
    #testAndSaveRounds()
    #testAndSaveVariance()

    #plotAccuracyByDistance()
    #plotAccuracyByShots()
    #plotAccuracyByRounds()
    plotAccuracyByVariance()

    plt.show()