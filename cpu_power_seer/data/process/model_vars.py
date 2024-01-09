import numpy as np


def get_formatted_vars(x_vars, data):
    x_values = []
    for i, var in enumerate(x_vars):
        x_values.append(data[var].values.reshape(-1, 1))
    x_stack = np.hstack(x_values)
    y = data["power"].values.reshape(-1, 1)
    return x_stack, y