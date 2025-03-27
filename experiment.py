import os
import pandas as pd
import matplotlib.pyplot as plt

from experimental_setup import ExperimentGenerator, Experimenter, Plotter, config

PROFILE_NAME = "quick"
TEST_DIR = "results"
TEST_FILE = f"{TEST_DIR}/{PROFILE_NAME}.csv"

ERROR_RATE_HEADER = "error_rate"
RUNTIME_HEADER = "runtime [s]"


# Expriments dataflow: generator makes a design, experimenter executes the experiments, plotter plots the results
#
# =================================================================================================
#      │                                                                                     
#      │ profile                                                  ┌─────────┐                
#      ▼               ┌──┬─────────────┐                         ├─────────┤                
# ┌─────────────┐      ├──┼─────────────┤    ┌────────────────┐   │         │   ┌───────────┐
# │  Generator  ├─────►│  │ Experiments ├───►│  Experimenter  ├──►│ Results ├──►│  Plotter  │
# └─────────────┘      └──┴─────────────┘    └────────────────┘   │         │   └───────────┘
#                                                                 │         │                
#                                                                 └─────────┘                
# =================================================================================================
if __name__ == "__main__":
    if not os.path.exists(TEST_FILE):
        testFrame = ExperimentGenerator.generateDesign(roundsAsDistance=True, profile=PROFILE_NAME)
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR)
        ExperimentGenerator.saveDesign(testFrame, TEST_FILE)

    testFrame = ExperimentGenerator.loadDesign(TEST_FILE)

    # Experiments loop
    for index, row in testFrame.iterrows():
        # If both error rate and runtime are already calculated, skip this row
        if not pd.isna(row[ERROR_RATE_HEADER]) and not pd.isna(row[RUNTIME_HEADER]):
            continue

        error_rate, runtime = Experimenter.execExperimentFromRow(row)

        # Save the results to the testFrame
        testFrame.at[index, ERROR_RATE_HEADER] = error_rate
        testFrame.at[index, RUNTIME_HEADER] = runtime

        ExperimentGenerator.saveDesign(testFrame, TEST_FILE, overwrite=True)

    # Results plotting
    testFrame = ExperimentGenerator.loadDesign(TEST_FILE)
    Plotter.plot(
        testFrame,
        fixedSubjects = { 
            "decoder": [config.SPARSE_BLOSSOM_DECODER], 
            "noiseModel": [config.SI1000_004_NOISE_MODEL] },
        variableFactor = "distance",
        variableSubject = "code",
        responseVariable = ERROR_RATE_HEADER,
        logScale = True
    )
    plt.show()