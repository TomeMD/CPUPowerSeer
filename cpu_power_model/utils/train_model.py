from cpu_power_model.config import config
from cpu_power_model.data.process import get_idle_consumption, get_formatted_vars
from cpu_power_model.data.model import Model


def run(train_timestamps, time_series):

    idle_consumption = get_idle_consumption(train_timestamps, config.train_range)
    X, y = get_formatted_vars(config.x_vars, time_series)

    return Model(config.model_name, idle_consumption, X, y)
