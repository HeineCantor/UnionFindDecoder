import numpy as np
import pandas as pd
import experimental_setup.config as config

from itertools import product

class DesignGenerator():
    def generateDesign(quick: bool = False) -> pd.DataFrame:
        doeDataframe = pd.DataFrame()
        
        subjects = config.SUBJECTS
        if quick:
            subjects = config.SUBJECTS_QUICK

        subjectNames = list(subjects.keys())

        # Set header
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
        factorLists = config.FACTORS.values()
        repetitions = range(config.REPETITIONS)

        combinations = list(product(*subjectLists, *factorLists, repetitions))

        # Generate design
        for combIndex, combination in enumerate(combinations):
            for subjectIndex, subjectName in enumerate(subjectNames):
                doeDataframe.at[combIndex, subjectName] = combination[subjectIndex]
            for factorIndex, factorName in enumerate(config.FACTORS.keys()):
                doeDataframe.at[combIndex, factorName] = combination[subjectIndex + factorIndex + 1]

            for constFactorName in config.CONSTANT_FACTORS.keys():
                doeDataframe.at[combIndex, constFactorName] = config.CONSTANT_FACTORS[constFactorName]

        return doeDataframe
