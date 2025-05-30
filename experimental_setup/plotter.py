import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Plotter():
    def plot(resultsFrame: pd.DataFrame, 
             fixedSubjects: dict, 
             variableFactor: str, 
             responseVariable: str,
             variableSubject : str = None, 
             secondaryVariableFactor: str = None,
             logScale: bool = False):
        plt.figure()
        plt.title(f"{responseVariable} by {variableFactor} | Fixed: {fixedSubjects}")
        plt.xlabel(f"{variableFactor}")
        plt.ylabel(f"{responseVariable}")
        
        filteredFrame = resultsFrame
        for subject, value in fixedSubjects.items():
            filteredFrame = filteredFrame[filteredFrame[subject].isin(value)]

        # Group by variableSubject in different frames
        if variableSubject is not None:
            for subject, group in filteredFrame.groupby(variableSubject):
                if secondaryVariableFactor is None:
                    plt.plot(
                        group[variableFactor],
                        group[responseVariable],
                        label=f"{responseVariable} {subject}",
                        marker="o"
                    )
                else:
                    for secondaryValue, secondaryGroup in group.groupby(secondaryVariableFactor):
                        plt.plot(
                            secondaryGroup[variableFactor],
                            secondaryGroup[responseVariable],
                            label=f"{responseVariable} {subject} {secondaryValue}",
                            marker="o"
                        )
        else:
            if secondaryVariableFactor is None:
                plt.plot(
                    filteredFrame[variableFactor],
                    filteredFrame[responseVariable],
                    label=f"{responseVariable}",
                    marker="o"
                )
            else:
                for secondaryValue, secondaryGroup in filteredFrame.groupby(secondaryVariableFactor):
                    plt.plot(
                        secondaryGroup[variableFactor],
                        secondaryGroup[responseVariable],
                        label=f"{responseVariable} {secondaryValue}",
                        marker="o"
                    )
                
        if logScale:
            plt.yscale("log")
        
        plt.xticks(np.unique(filteredFrame[variableFactor]))
        plt.grid()
        plt.legend()