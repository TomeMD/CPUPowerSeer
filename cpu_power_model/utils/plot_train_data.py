from cpu_power_model.config import config
from cpu_power_model.data.plot import plot_time_series, plot_var


def run(temp_series, time_series):
    config.img_dir = config.train_dir
    plot_var("CPU Temperature", temp_series, "temp", f'{config.model_name}-temperature-data.png')
    plot_time_series("Train Time Series", time_series, config.x_vars, f'{config.model_name}-train-data.png')
