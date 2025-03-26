import numpy as np
import pandas as pd
import experimental_setup.config as config
import os

from itertools import product

# TODO: separare csv di esperimenti e risultati (perché?)
class ExperimentGenerator():
    def generateDesign(
            roundsAsDistance: bool = True, 
            quick: bool = False
        ) -> pd.DataFrame:
        '''
        Generates a dataframe with all the possible combinations of the factors

        Parameters:
            roundsAsDistance (bool): If True, the number of rounds is the distance (a volume d^3). If False, rounds are taken from factors range in config (a volume r*d^2).
        '''

        doeDataframe = pd.DataFrame()
        
        # TODO: change to profile management
        subjects = config.SUBJECTS
        if quick:
            subjects = config.SUBJECTS_QUICK

        subjectNames = list(subjects.keys())

        # Setting table header
        for subjectName in subjectNames:
            doeDataframe[subjectName] = ""

        for factorName in config.CONSTANT_FACTORS.keys():
            doeDataframe[factorName] = config.CONSTANT_FACTORS[factorName]

        for factorName in config.FACTORS.keys():
            doeDataframe[factorName] = ""

        for responseVariable in config.RESPONSE_VARIABLES:
            doeDataframe[responseVariable] = ""

        # Generate subject combinations
        subjectLists = subjects.values()

        if roundsAsDistance:
            factorLists = [values for key, values in config.FACTORS.items() if key != "rounds"]
        else:
            factorLists = config.FACTORS.values()

        repetitions = range(config.REPETITIONS)

        # Full factorial design {subjects} x {variable factors} x {repetitions}
        combinations = list(product(*subjectLists, *factorLists, repetitions))

        # Generate experiment table
        for combIndex, combination in enumerate(combinations):
            for subjectIndex, subjectName in enumerate(subjectNames):
                doeDataframe.at[combIndex, subjectName] = combination[subjectIndex]

            for factorIndex, factorName in enumerate(config.FACTORS.keys()):
                doeDataframe.at[combIndex, factorName] = combination[subjectIndex + factorIndex + 1]

            for constFactorName in config.CONSTANT_FACTORS.keys():
                doeDataframe.at[combIndex, constFactorName] = config.CONSTANT_FACTORS[constFactorName]

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