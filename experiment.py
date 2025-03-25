import os
import matplotlib.pyplot as plt

from experimental_setup.design_generator import DesignGenerator
from experimental_setup.prelim_accuracy import accuracyByDistance, accuracyByShots, accuracyByRounds, accuracyVariance
from experimental_setup.plotter import plotAccuracyByDistance, plotAccuracyByRounds, plotAccuracyByShots, plotAccuracyByVariance, plotDistributionVariance, plotRuntimeByDistance

BASE_RESULT_SAVE_PATH = "./experimental_setup/results/results_"

def saveFile(data, path, overwrite=False):
    if not overwrite and os.path.exists(path):
        print(f"File {path} already exists. Skipping.")
    else:
        with open(path, "w") as file:
            file.write(str(data).replace('),','),\n'))

def generateAndExecuteDesign():
    design = DesignGenerator.generateDesign()
    print(design)

def executePreliminaryDesign(codeType, decoder, overwrite=False):
    if not os.path.exists(BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}"):
        os.makedirs(BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}")

    distancePath = BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}/results_distance.txt"
    if not overwrite and os.path.exists(distancePath):
        print(f"File {distancePath} already exists. Skipping.")
    else:
        statsDistance = accuracyByDistance(codeType, decoder)
        saveFile(statsDistance, distancePath, overwrite)

    shotsPath = BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}/results_shots.txt"
    if not overwrite and os.path.exists(shotsPath):
        print(f"File {shotsPath} already exists. Skipping.")
    else:
        statsShots = accuracyByShots(codeType, decoder)
        saveFile(statsShots, shotsPath, overwrite)

    roundsPath = BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}/results_rounds.txt"
    if not overwrite and os.path.exists(roundsPath):
        print(f"File {roundsPath} already exists. Skipping.")
    else:
        statsRounds = accuracyByRounds(codeType, decoder)
        saveFile(statsRounds, roundsPath, overwrite)

    variancePath = BASE_RESULT_SAVE_PATH + f"{codeType}_{decoder}/results_variance.txt"
    if not overwrite and os.path.exists(variancePath):
        print(f"File {variancePath} already exists. Skipping.")
    else:
        statsVariance = accuracyVariance(codeType, decoder)
        saveFile(statsVariance, variancePath, overwrite)

def plotPreliminaryDesign(codeType, decoders):
    # if type(decoders) != list:
    #     plotAccuracyByVariance(codeType, decoders)
    #     plotDistributionVariance(codeType, decoders)
    #     decoders = [decoders]

    # plotAccuracyByDistance(codeType, decoders)
    # plotAccuracyByShots(codeType, decoders)
    # plotAccuracyByRounds(codeType, decoders)

    plotRuntimeByDistance(codeType, decoders)

    plt.show()

if __name__ == "__main__":
    # generateAndExecuteDesign()
    # executePreliminaryDesign('surface_code:rotated_memory_z', 'pymatching')
    # executePreliminaryDesign('surface_code:rotated_memory_z', 'fusion_blossom')
    # executePreliminaryDesign('surface_code:rotated_memory_z', 'union_find_decoder')
    # plotPreliminaryDesign('surface_code:rotated_memory_z', 'pymatching')
    # plotPreliminaryDesign('surface_code:rotated_memory_z', 'fusion_blossom')
    # plotPreliminaryDesign('surface_code:rotated_memory_z', 'union_find_decoder')
    plotPreliminaryDesign('surface_code:rotated_memory_z', ['pymatching', 'union_find_decoder'])