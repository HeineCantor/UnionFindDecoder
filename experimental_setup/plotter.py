import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Plotter():
    def plot(resultsFrame: pd.DataFrame, fixedSubjects: dict, variableFactor: str, responseVariable: str, fixedFactors: dict = {},
             logScale: bool = False):
        plt.figure()
        plt.title(f"{responseVariable} by {variableFactor}")
        plt.xlabel(f"{variableFactor}")
        plt.ylabel(f"{responseVariable}")
        
        plt.plot(
            resultsFrame[variableFactor],
            resultsFrame[responseVariable],
            label=f"{responseVariable}",
            marker="o"
        )

        if logScale:
            plt.yscale("log")
        
        plt.grid()
        plt.legend()