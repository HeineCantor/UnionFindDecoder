import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

class Plotter():
    def plot(
            resultsFrame: pd.DataFrame, 
            fixedSubjects: dict, 
            variableFactor: str, 
            responseVariable: str,
            variableSubject : str = None, 
            secondaryVariableFactor: str = None,
            logScaleY: bool = False,
            logScaleX: bool = False,
            customTitle: str = None,
            customXLabel: str = None,
            customYLabel: str = None,
            avoidZero: bool = False
        ):
        fig = plt.figure()
        
        plt.title(f"{responseVariable} by {variableFactor} | Fixed: {fixedSubjects}", fontsize=16)
        if customTitle:
            plt.title(customTitle, fontsize=16)

        plt.xlabel(f"{variableFactor}", fontsize=14)
        if customXLabel:
            plt.xlabel(customXLabel, fontsize=14)

        plt.ylabel(f"{responseVariable}", fontsize=14)
        if customYLabel:
            plt.ylabel(customYLabel, fontsize=14)

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        
        filteredFrame = resultsFrame
        for subject, value in fixedSubjects.items():
            filteredFrame = filteredFrame[filteredFrame[subject].isin(value)]

        # Group by variableSubject in different frames
        if variableSubject is not None:
            for subject, group in filteredFrame.groupby(variableSubject):
                if responseVariable == "runtime [s]":
                    group[responseVariable] = group[responseVariable] / group["shots"]
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
                            label=f"{secondaryVariableFactor}={secondaryValue}",
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
                        label=f"{secondaryValue}",
                        marker="o"
                    )
                
        if logScaleY:
            plt.yscale("log")
        if logScaleX:
            plt.xscale("log")

        fig.set_dpi(280)
        plt.xticks(np.unique(filteredFrame[variableFactor]))
        plt.grid()
        plt.legend(fontsize=8, loc='lower right')