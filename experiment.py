import os
import pandas as pd
import matplotlib.pyplot as plt

from experimental_setup import ExperimentGenerator, Experimenter, Plotter, config

PROFILE_NAME = "dse_peeling_only"
TEST_DIR = "results"
TEST_FILE = f"{TEST_DIR}/{PROFILE_NAME}.csv"

ERROR_RATE_HEADER = "logical_error_rate"
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
        testFrame = ExperimentGenerator.generateDesign(profile=PROFILE_NAME)
        if not os.path.exists(TEST_DIR):
            os.makedirs(TEST_DIR)
        ExperimentGenerator.saveDesign(testFrame, TEST_FILE)

    testFrame = ExperimentGenerator.loadDesign(TEST_FILE)

    # Experiments loop
    for index, row in testFrame.iterrows():
        # If both error rate and runtime are already calculated, skip this row
        if not pd.isna(row[ERROR_RATE_HEADER]) and not pd.isna(row[RUNTIME_HEADER]):
            continue

        kwargs = dict()
        if "dse" in PROFILE_NAME:
            if "early_stopping" in row:
                kwargs["early_stopping_param"] = row["early_stopping"]
            if "early_stopping_peeling" in row:
                kwargs["early_stopping_peeling_param"] = row["early_stopping_peeling"]

        error_rate, runtime = Experimenter.execExperimentFromRow(row, **kwargs)

        # Save the results to the testFrame
        testFrame.at[index, ERROR_RATE_HEADER] = error_rate
        testFrame.at[index, RUNTIME_HEADER] = runtime

        ExperimentGenerator.saveDesign(testFrame, TEST_FILE, overwrite=True)

    # Results plotting
    testFrame = ExperimentGenerator.loadDesign(TEST_FILE)
    # Plotter.plot(
    #     testFrame,
    #     fixedSubjects = { 
    #         "decoder": [config.UF_ARCH_DECODER], 
    #         "noiseModel": [config.SI1000_NOISE_MODEL] },
    #     variableFactor = "base_error_rate",
    #     variableSubject = "code",
    #     responseVariable = ERROR_RATE_HEADER,
    #     secondaryVariableFactor = "distance",
    #     logScaleY = True,
    #     logScaleX = True,
    #     customTitle = "Logical Error Rate by Physical Error Rate",
    #     customXLabel = "Physical Error Rate",
    #     customYLabel = "Logical Error Rate",
    #     avoidZero=True
    # )
    Plotter.plot(
        testFrame,
        fixedSubjects = { 
            "decoder": [config.UF_ARCH_DECODER], 
            "noiseModel": [config.SI1000_NOISE_MODEL],
            "distance": [17]
        },
        variableFactor = "early_stopping_peeling",
        variableSubject = "code",
        responseVariable = ERROR_RATE_HEADER,
        secondaryVariableFactor = "base_error_rate",
        logScaleY = True,
        customTitle = "Logical Error Rate by E_P (d=17)",
        customXLabel = "E_P",
        customYLabel = "Logical Error Rate",
    )
    plt.show()