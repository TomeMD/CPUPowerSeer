from cpu_power_model.config import config
from cpu_power_model.data.process import parse_timestamps, get_time_series
from cpu_power_model.logs.logger import log


def run():

    log(f"Parsing train timestamps from {config.f_train_timestamps}")
    train_timestamps = parse_timestamps(config.f_train_timestamps)

    log("Getting temperature time series from corresponding period")
    temp_series = get_time_series(["temp"], train_timestamps, config.train_range, True)

    log("Getting model variables time series from corresponding period")
    time_series = get_time_series(config.x_vars + ["energy"], train_timestamps, config.train_range)

    return train_timestamps, temp_series, time_series
