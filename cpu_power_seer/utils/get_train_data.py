from cpu_power_seer.config import config
from cpu_power_seer.data.process.timestamps import parse_timestamps
from cpu_power_seer.data.process.time_series import get_time_series
from cpu_power_seer.logs.logger import log


def run():

    log(f"Parsing train timestamps from {config.train_ts_file}")
    train_timestamps = parse_timestamps(config.train_ts_file)

    log("Getting temperature time series from corresponding period")
    temp_series = get_time_series(["temp"], train_timestamps, include_idle=True)

    log("Getting model variables time series from corresponding period")
    time_series = get_time_series(config.x_vars + ["power"], train_timestamps)

    return train_timestamps, temp_series, time_series
