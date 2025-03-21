import stim, sinter
import matplotlib.pyplot as plt
import numpy as np

RESULTS_PATH = "experimental_setup/results/results_05/"

def _plotAccuracyBy(stats, xAxis, yAxis, parameterName, log=True, meanAndStdDev=False):
    p = stats[0].json_metadata['p']
    errorModelName = stats[0].json_metadata['error_model']
    shots = stats[0].shots
    rounds = stats[0].json_metadata['r']
    distance = stats[0].json_metadata['d']

    plt.figure()

    if log:
        plt.yscale('log')

    plt.plot(xAxis, yAxis, marker='o', label=f"Logical error rate")
    plt.xlabel(parameterName)
    plt.ylabel("Accuracy")
    plt.title(f"Accuracy by {parameterName} - p={p} - {errorModelName} | Shots={shots} | Rounds={rounds} | d={distance}")

    if meanAndStdDev:
        stdDev = np.std(yAxis)
        mean = np.mean(yAxis)

        print(f"{parameterName} TEST | Mean: {mean}, Std Dev: {stdDev}")

        plt.axhline(y=mean, color='r', linestyle='--', label='Mean error rate')
        plt.axhline(y=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
        plt.axhline(y=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')

    plt.xticks(xAxis)

    plt.axhline(y=1-p, color='r', linestyle='--', label='Base error rate')

    plt.grid()
    plt.legend()

def plotAccuracyByDistance(codeType, decoder):
    with open(f"./experimental_setup/results/results_{codeType}_{decoder}/results_distance.txt", "r") as f:
        stats = eval(f.read())

    distanceDict = {}

    for stat in stats:
        stat = stat[0] # Unpack the list
        distance = stat.json_metadata['d']
        if distance not in distanceDict:
            distanceDict[distance] = []
        distanceDict[distance] = 1 - stat.errors / stat.shots

    distanceDict = dict(sorted(distanceDict.items()))

    xAxis = list(distanceDict.keys())
    yAxis = list(distanceDict.values())

    _plotAccuracyBy(stats[0], xAxis, yAxis, "Distance", log=True)

def plotAccuracyByShots(codeType, decoder):
    with open(f"./experimental_setup/results/results_{codeType}_{decoder}/results_shots.txt", "r") as f:
        stats = eval(f.read())

    shotsDict = {}

    for stat in stats:
        shots = stat.shots
        if shots not in shotsDict:
            shotsDict[shots] = []
        shotsDict[shots] = 1 - stat.errors / stat.shots

    shotsDict = dict(sorted(shotsDict.items()))

    xAxis = list(shotsDict.keys())
    yAxis = list(shotsDict.values())

    mean = np.mean(yAxis)
    stdDev = np.std(yAxis)

    _plotAccuracyBy(stats, xAxis, yAxis, "Shots", meanAndStdDev=True)

def plotAccuracyByRounds(codeType, decoder):
    with open(f"./experimental_setup/results/results_{codeType}_{decoder}/results_rounds.txt", "r") as f:
        stats = eval(f.read())

    roundsDict = {}

    for stat in stats:
        rounds = stat.json_metadata['r']
        if rounds not in roundsDict:
            roundsDict[rounds] = []
        roundsDict[rounds] = 1 - stat.errors / stat.shots

    roundsDict = dict(sorted(roundsDict.items()))

    xAxis = list(roundsDict.keys())
    yAxis = list(roundsDict.values())

    _plotAccuracyBy(stats, xAxis, yAxis, "Rounds", log=False)

def plotAccuracyByVariance(codeType, decoder):
    with open(f"./experimental_setup/results/results_{codeType}_{decoder}/results_variance.txt", "r") as f:
        stats = eval(f.read())

    varianceDict = {}
    for i, stat in enumerate(stats):
        stat = stat[0]
        varianceDict[i] = 1 - stat.errors / stat.shots

    xAxis = list(varianceDict.keys())
    yAxis = list(varianceDict.values())

    stdDev = np.std(yAxis)
    mean = np.mean(yAxis)

    print(f"VARIANCE TEST | Mean: {mean}, Std Dev: {stdDev}")

    plt.figure()
    plt.plot(xAxis, yAxis, marker='o', label=f"Logical error rate")
    plt.xlabel("Repetition")
    plt.ylabel("Accuracy")
    plt.axhline(y=mean, color='r', linestyle='--', label='Mean error rate')
    plt.axhline(y=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
    plt.axhline(y=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')
    plt.title(f"Accuracy by Repetition")
    plt.grid()

def plotDistributionVariance(codeType, decoder):
    with open(f"./experimental_setup/results/results_{codeType}_{decoder}/results_variance.txt", "r") as f:
        stats = eval(f.read())

    varianceDict = {}
    for i, stat in enumerate(stats):
        stat = stat[0]
        varianceDict[i] = 1 - stat.errors / stat.shots

    xAxis = list(varianceDict.keys())
    yAxis = list(varianceDict.values())

    fig, axs = plt.subplots(3)
    fig.suptitle('Shots distribution')

    binNum = 51
    bins = np.histogram(yAxis, bins=binNum)[1]

    stdDev = np.std(yAxis[:30])
    mean = np.mean(yAxis[:30])
    median = np.median(yAxis[:30])

    axs[0].hist(yAxis[:30], bins=bins, edgecolor='black')
    axs[0].set_title('Error rate by 30 repetitions')
    axs[0].set_xlabel("Repetition")
    axs[0].set_ylabel("Accuracy")
    axs[0].axvline(x=mean, color='r', linestyle='--', label='Mean error rate')
    axs[0].axvline(x=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
    axs[0].axvline(x=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')
    axs[0].axvline(x=median, color='b', linestyle='--', label='Median error rate')
    axs[0].set_xlim([np.min(yAxis), np.max(yAxis)])
    axs[0].legend()

    stdDev = np.std(yAxis[:50])
    mean = np.mean(yAxis[:50])
    median = np.median(yAxis[:50])

    axs[1].hist(yAxis[:50], bins=bins, edgecolor='black')
    axs[1].set_title('Error rate by 50 repetitions')
    axs[1].set_xlabel("Repetition")
    axs[1].set_ylabel("Accuracy")
    axs[1].axvline(x=mean, color='r', linestyle='--', label='Mean error rate')
    axs[1].axvline(x=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
    axs[1].axvline(x=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')
    axs[1].axvline(x=median, color='b', linestyle='--', label='Median error rate')
    axs[1].set_xlim([np.min(yAxis), np.max(yAxis)])

    stdDev = np.std(yAxis[:100])
    mean = np.mean(yAxis[:100])
    median = np.median(yAxis[:100])

    axs[2].hist(yAxis[:100], bins=bins, edgecolor='black')
    axs[2].set_title('Error rate by 100 repetitions')
    axs[2].set_xlabel("Repetition")
    axs[2].set_ylabel("Accuracy")
    axs[2].axvline(x=mean, color='r', linestyle='--', label='Mean error rate')
    axs[2].axvline(x=mean + stdDev, color='g', linestyle='--', label='Mean error rate + std dev')
    axs[2].axvline(x=mean - stdDev, color='g', linestyle='--', label='Mean error rate - std dev')
    axs[2].axvline(x=median, color='b', linestyle='--', label='Median error rate')
    axs[2].set_xlim([np.min(yAxis), np.max(yAxis)])
