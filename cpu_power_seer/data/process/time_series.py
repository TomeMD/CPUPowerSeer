import warnings
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading

from cpu_power_seer.config import config
from cpu_power_seer.logs.logger import log
from cpu_power_seer.influxdb.influxdb_queries import var_query
from cpu_power_seer.influxdb.influxdb import query_influxdb

current_vars = []
OUT_RANGE = 1.5

warnings.simplefilter(action='ignore', category=FutureWarning)


# Time unit fixer, it only adjusts forward, i.e. from seconds/minutes to minutes/hours
def fix_time_units(df, current, prev):
    if current == "hours" and prev == "seconds":
        df["time_diff"] = df["time_diff"] / 3600
    else:
        df["time_diff"] = df["time_diff"] / 60
    df["time_unit"] = current
    log(f"Test time series time units have been modified from {prev} to {current}", "WARN")
    return df


# Add time_diff column which represents time instead of dates
def set_time_diff(df, time_column, initial_date=None):
    first_date = initial_date if initial_date is not None else df[time_column].min()
    last_date = df[time_column].max()
    time_diff = (df[time_column] - first_date)
    total_duration = last_date - first_date

    # Depending on time series duration different time units are used
    if total_duration < pd.Timedelta(hours=1):
        df["time_diff"] = time_diff.dt.total_seconds()
        df["time_unit"] = 'seconds'
    elif total_duration < pd.Timedelta(hours=12):
        df["time_diff"] = time_diff.dt.total_seconds() / 60
        df["time_unit"] = 'minutes'
    else:
        df["time_diff"] = time_diff.dt.total_seconds() / 3600
        df["time_unit"] = 'hours'


# Remove outliers for a specified column
def remove_outliers(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - OUT_RANGE * iqr
    upper_bound = q3 + OUT_RANGE * iqr
    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df_filtered


# Get data for a given period (obtained from timestamps)
def get_experiment_data(timestamp):
    global current_vars
    tid = threading.get_ident()
    start_date, stop_date, exp_type = timestamp
    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    stop_str = stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    if config.verbose:
        log(f"[Thread {tid}] Querying data to InfluxDB between {start_str} and {stop_str}")

    # Get current_vars time series and merge data
    exp_data = pd.DataFrame()
    for var in current_vars:
        df = query_influxdb(var_query[var], start_str, stop_str, config.influxdb_bucket)
        if not df.empty:
            df = remove_outliers(df, "_value")
            df.rename(columns={'_value': var}, inplace=True)
            df = df[["_time", var]]
            if exp_data.empty:
                exp_data = df
            else:
                exp_data = pd.merge(exp_data, df, on='_time')
    exp_data.rename(columns={'_time': 'time'}, inplace=True)

    # Remove DataFrame useless variables
    try:
        exp_data = exp_data[current_vars + ["time"]]
    except KeyError:
        log(f"[Thread {tid}] Error getting data between {start_date} and {stop_date}", "ERR")
        print(exp_data)
        exit(1)
    return exp_data


# Parallelise data retrieval from InfluxDB
def get_parallel_time_series(_vars, timestamps):
    global current_vars
    current_vars = _vars.copy()
    time_series = pd.DataFrame(columns=current_vars)

    executor = ThreadPoolExecutor()
    results = executor.map(get_experiment_data, timestamps)
    executor.shutdown()

    for result in results:
        result.dropna(inplace=True)
        time_series = pd.concat([time_series, result], ignore_index=True)

    return time_series


# Get _vars time series from timestamps
def get_time_series(_vars, timestamps, include_idle=False, initial_date=None):
    # Remove idle periods when include_idle is false
    filtered_timestamps = [t for t in timestamps if include_idle or t[2] != "IDLE"]
    time_series = get_parallel_time_series(_vars, filtered_timestamps)

    # Add time_diff column
    set_time_diff(time_series, "time", initial_date)
    return time_series


# Get idle consumption from timestamps
def get_idle_consumption(timestamps):
    # Get power only from idle periods
    filtered_timestamps = [t for t in timestamps if t[2] == "IDLE"]
    time_series = get_parallel_time_series(["power"], filtered_timestamps)

    return time_series["power"].mean()


