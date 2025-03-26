import os
import pandas as pd

from experimental_setup.experiment_generator import ExperimentGenerator
from experimental_setup.experimenter import Experimenter

PROFILE_NAME = "preliminary_distance"
TEST_FILE = f"{PROFILE_NAME}.csv"

ERROR_RATE_HEADER = "error_rate"
RUNTIME_HEADER = "runtime [s]"

# TODO: dataflow delle chiamate per fare capire bene (stilizza il grafico su Docs Slides)
if __name__ == "__main__":
    if not os.path.exists(TEST_FILE):
        testFrame = ExperimentGenerator.generateDesign(roundsAsDistance=False, profile=PROFILE_NAME)
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