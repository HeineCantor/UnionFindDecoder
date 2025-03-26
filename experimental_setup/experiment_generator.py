import numpy as np
import pandas as pd
import experimental_setup.config as config
import os

from itertools import product

# TODO: separare csv di esperimenti e risultati (perché?)
class ExperimentGenerator():
    def generateDesign(
            roundsAsDistance: bool = True, 
            profile: str = "full"
        ) -> pd.DataFrame:
        '''
        Generates a dataframe with all the possible combinations of the factors

        Parameters:
            roundsAsDistance (bool): If True, the number of rounds is the distance (a volume d^3). If False, rounds are taken from factors range in config (a volume r*d^2).
        '''

        doeDataframe = pd.DataFrame()
        
        selectedProfile = config.profiles[profile]

        subjectsDict = selectedProfile["subjects"]
        factorsDict = selectedProfile["factors"]
        constantFactorsDict = selectedProfile["constant_factors"]
        responseVariablesDict = selectedProfile["response_variables"]
        repetitionsValue = selectedProfile["repetitions"]

        subjectNames = list(subjectsDict.keys())

        # Setting table header
        for subjectName in subjectNames:
            doeDataframe[subjectName] = ""

        for factorName in constantFactorsDict.keys():
            doeDataframe[factorName] = constantFactorsDict[factorName]

        for factorName in factorsDict.keys():
            doeDataframe[factorName] = ""

        for responseVariable in responseVariablesDict:
            doeDataframe[responseVariable] = ""

        # Generate subject combinations
        subjectLists = subjectsDict.values()

        if roundsAsDistance:
            factorLists = [values for key, values in factorsDict.items() if key != "rounds"]
        else:
            factorLists = factorsDict.values()

        repetitions = range(repetitionsValue)

        # Full factorial design {subjects} x {variable factors} x {repetitions}
        combinations = list(product(*subjectLists, *factorLists, repetitions))

        # Generate experiment table
        for combIndex, combination in enumerate(combinations):
            for subjectIndex, subjectName in enumerate(subjectNames):
                doeDataframe.at[combIndex, subjectName] = combination[subjectIndex]

            for factorIndex, factorName in enumerate(factorsDict.keys()):
                doeDataframe.at[combIndex, factorName] = combination[subjectIndex + factorIndex + 1]

            for constFactorName in constantFactorsDict.keys():
                doeDataframe.at[combIndex, constFactorName] = constantFactorsDict[constFactorName]

        if roundsAsDistance:
            doeDataframe["rounds"] = doeDataframe["distance"]

        return doeDataframe

    def saveDesign(doeDataframe: pd.DataFrame, filename: str, overwrite: bool = False):
        if not overwrite:
            if os.path.exists(filename):
                raise FileExistsError("File already exists. Set overwrite=True to overwrite it.")
        doeDataframe.to_csv(filename, index=False)

    def loadDesign(filename: str) -> pd.DataFrame:
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found.")
        return pd.read_csv(filename)