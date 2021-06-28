import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

pd.options.plotting.backend = "plotly"

class Visualizer:
    def __init__(self):
        pass

    def visualize(self, df_plot, title, labels):
        fig = df_plot.plot(title=title, labels=labels)
        fig.show()
