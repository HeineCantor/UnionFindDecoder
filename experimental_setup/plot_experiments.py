import stim, sinter
import matplotlib.pyplot as plt
import numpy as np

RESULTS_PATH = "results_onlym_3/"
RESULTS_PATH = ""

def _plotAccuracyBy(stats, xAxis, yAxis, parameterName, log=True, meanAndStdDev=False):
    p = stats[0].json_metadata['p']
    errorModelName = stats[0].json_metadata['error_model']
    shots = stats[0].shots
    rounds = stats[0].json_metadata['r']
    distance = stats[0].json_metadata['d']

    plt.figure()
    plt.plot(xAxis, yAxis, marker='o', label=f"Logical error rate")
    plt.xlabel(parameterName)
    plt.ylabel("Error rate")
    plt.title(f"Accuracy by {parameterName} - p={p} - {errorModelName} | Shots={shots} | Rounds={rounds} | d={distance}")

    if log:
        plt.yscale('log')

    if meanAndStdDev:
        stdDev = np.std(yAxis)
        mean = np.mean(yAxis)

        print(f"{parameterName} TEST | Mean: {mean}, Std Dev: {stdDev}")

        plt.axhline(y=mean, color='r', linestyle='--', label='Mean error rate')
        plt.axhline(y=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
        plt.axhline(y=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')

    plt.xticks(xAxis)

    plt.axhline(y=p, color='r', linestyle='--', label='Base error rate')

    plt.grid()
    plt.legend()

def plotAccuracyByDistance():
    with open(RESULTS_PATH + "results_distance.txt", "r") as f:
        stats = eval(f.read())

    distanceDict = {}

    for stat in stats:
        distance = stat.json_metadata['d']
        if distance not in distanceDict:
            distanceDict[distance] = []
        distanceDict[distance] = stat.errors / stat.shots

    distanceDict = dict(sorted(distanceDict.items()))

    xAxis = list(distanceDict.keys())
    yAxis = list(distanceDict.values())

    _plotAccuracyBy(stats, xAxis, yAxis, "Distance")

def plotAccuracyByShots():
    with open(RESULTS_PATH + "results_shots.txt", "r") as f:
        stats = eval(f.read())

    shotsDict = {}

    for stat in stats:
        shots = stat.shots
        if shots not in shotsDict:
            shotsDict[shots] = []
        shotsDict[shots] = stat.errors / stat.shots

    shotsDict = dict(sorted(shotsDict.items()))

    xAxis = list(shotsDict.keys())
    yAxis = list(shotsDict.values())

    mean = np.mean(yAxis)
    stdDev = np.std(yAxis)

    _plotAccuracyBy(stats, xAxis, yAxis, "Shots", meanAndStdDev=True)

def plotAccuracyByRounds():
    with open(RESULTS_PATH + "results_rounds.txt", "r") as f:
        stats = eval(f.read())

    roundsDict = {}

    for stat in stats:
        rounds = stat.json_metadata['r']
        if rounds not in roundsDict:
            roundsDict[rounds] = []
        roundsDict[rounds] = stat.errors / stat.shots

    roundsDict = dict(sorted(roundsDict.items()))

    xAxis = list(roundsDict.keys())
    yAxis = list(roundsDict.values())

    _plotAccuracyBy(stats, xAxis, yAxis, "Rounds", log=False)

def plotAccuracyByVariance():
    with open(RESULTS_PATH + "results_variance.txt", "r") as f:
        stats = eval(f.read())

    varianceDict = {}
    for i, stat in enumerate(stats):
        stat = stat[0]
        varianceDict[i] = stat.errors / stat.shots

    xAxis = list(varianceDict.keys())
    yAxis = list(varianceDict.values())

    stdDev = np.std(yAxis)
    mean = np.mean(yAxis)

    print(f"VARIANCE TEST | Mean: {mean}, Std Dev: {stdDev}")

    plt.figure()
    plt.plot(xAxis, yAxis, marker='o', label=f"Logical error rate")
    plt.xlabel("Repetition")
    plt.ylabel("Error rate")
    plt.axhline(y=mean, color='r', linestyle='--', label='Mean error rate')
    plt.axhline(y=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
    plt.axhline(y=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')
    plt.title(f"Accuracy by Repetition")
    plt.grid()

if __name__ == "__main__":
    #plotAccuracyByDistance()
    #plotAccuracyByShots()
    plotAccuracyByRounds()
    #plotAccuracyByVariance()

    plt.show()
