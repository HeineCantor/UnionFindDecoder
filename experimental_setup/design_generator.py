import numpy as np
import pandas as pd

from itertools import product

# === Subject: Codes ===
SUBJECT_CODES = [ "unrotated", "rotated", "unrotated_xzzx", "rotated_xzzx" ]

# === Subject: Decoders ===
SUBJECT_DECODERS = [ "sparse_blossom", "union_find" ]

SUBJECTS = {
    "code" : SUBJECT_CODES,
    "decoder" : SUBJECT_DECODERS
}

SUBJECTS_QUICK = {
    "code" : [ "rotated" ],
    "decoder" : [ "sparse_blossom" ]
}

# === Factors ===

#   === Constant Factors ===
CONSTANT_FACTORS = { 
    "p" : 0.05 , 
    "shots" : 10000, 
    "rounds" : 100 
}

#   === Variable Factors ===
FACTORS = { 
    "distance" : range(3, 31 + 1, 2),
}

# === Response Variables ===

RESPONSE_VARIABLES = [ "error_rate", "runtime" ]

def generateDesign(quick: bool = False) -> pd.DataFrame:
    doeDataframe = pd.DataFrame()
    
    subjects = SUBJECTS
    if quick:
        subjects = SUBJECTS_QUICK

    subjectNames = list(subjects.keys())

    # Set header
    for subjectName in subjectNames:
        doeDataframe[subjectName] = ""

    for factorName in CONSTANT_FACTORS.keys():
        doeDataframe[factorName] = CONSTANT_FACTORS[factorName]

    for factorName in FACTORS.keys():
        doeDataframe[factorName] = ""

    for responseVariable in RESPONSE_VARIABLES:
        doeDataframe[responseVariable] = ""

    # Generate subject combinations
    subjectLists = subjects.values()
    factorLists = FACTORS.values()
    combinations = list(product(*subjectLists, *factorLists))

    # Generate design
    for combIndex, combination in enumerate(combinations):
        for subjectIndex, subjectName in enumerate(subjectNames):
            doeDataframe.at[combIndex, subjectName] = combination[subjectIndex]
        for factorIndex, factorName in enumerate(FACTORS.keys()):
            doeDataframe.at[combIndex, factorName] = combination[subjectIndex + factorIndex + 1]

        for constFactorName in CONSTANT_FACTORS.keys():
            doeDataframe.at[combIndex, constFactorName] = CONSTANT_FACTORS[constFactorName]

    return doeDataframe

if __name__ == "__main__":
    dfDesign = generateDesign()
    dfDesign.to_csv("design.csv", index=False)
