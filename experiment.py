import os
import pandas as pd
import matplotlib.pyplot as plt

from experimental_setup import ExperimentGenerator, Experimenter, Plotter

PROFILE_NAME = "mock"
TEST_FILE = f"results/{PROFILE_NAME}.csv"

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
        ExperimentGenerator.saveDesign(testFrame, TEST_FILE)

    testFrame = ExperimentGenerator.loadDesign(TEST_FILE)
    for index, row in testFrame.iterrows():
        current_error_rate = row[ERROR_RATE_HEADER]
        current_runtime = row[RUNTIME_HEADER]

        if not pd.isna(current_error_rate) and not pd.isna(current_runtime):
            continue

        error_rate, runtime = Experimenter.execExperiment(
            [row["distance"]],
            [row["shots"]],
            [row["rounds"]],
            row["code"],
            row["decoder"],
            row["noiseModel"]
        )

        print(f"Error rate: {error_rate}, Runtime: {runtime}")
        testFrame.at[index, ERROR_RATE_HEADER] = error_rate
        testFrame.at[index, RUNTIME_HEADER] = runtime
        ExperimentGenerator.saveDesign(testFrame, TEST_FILE, overwrite=True)

    testFrame = ExperimentGenerator.loadDesign("results/mock.csv")
    Plotter.plot(
        testFrame,
        fixedSubjects = { "code": ["rotated"], "decoder": ["sparse_blossom"], "noiseModel": ["willow"] },
        variableFactor = "distance",
        responseVariable = ERROR_RATE_HEADER
    )
    plt.show()