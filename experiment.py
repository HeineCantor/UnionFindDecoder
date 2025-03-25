import os

from experimental_setup.design_generator import DesignGenerator

TEST_FILE = "test.csv"

if __name__ == "__main__":
    if not os.path.exists(TEST_FILE):
        testFrame = DesignGenerator.generateDesign(roundsAsDistance=True)
        DesignGenerator.saveDesign(testFrame, TEST_FILE)

    testFrame = DesignGenerator.loadDesign(TEST_FILE)
    