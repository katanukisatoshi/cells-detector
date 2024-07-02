import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display

def display_dataframe_to_user(name: str, dataframe: pd.DataFrame):
    """
    Function to display a DataFrame and a plot.

    Parameters:
    name (str): The title of the display.
    dataframe (pd.DataFrame): The DataFrame to display.
    """
    print(f"Displaying DataFrame: {name}")
    display(dataframe)
    dataframe.plot(kind='bar', x=dataframe.columns[0], y=dataframe.columns[1], legend=False)
    plt.title(name)
    plt.xlabel(dataframe.columns[0])
    plt.ylabel(dataframe.columns[1])
    plt.show()
