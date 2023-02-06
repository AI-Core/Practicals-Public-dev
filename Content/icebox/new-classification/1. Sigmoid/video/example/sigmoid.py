import numpy as np
import plotly.express as px


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


print(sigmoid(-1000))
print(sigmoid(0))
print(sigmoid(1000))
