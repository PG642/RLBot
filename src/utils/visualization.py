import pandas as pd

pd.options.plotting.backend = "plotly"


def visualize(df_plot, title, labels):
    fig = df_plot.plot(title=title, labels=labels)
    fig.show()
