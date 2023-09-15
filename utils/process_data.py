import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.influxdb import *


def parse_timestamps(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()
    timestamps = []
    for i in range(0, len(lines), 2):
        start_line = lines[i]
        stop_line = lines[i+1]
        start_str = " ".join(start_line.split(" ")[-2:]).strip()
        stop_str = " ".join(stop_line.split(" ")[-2:]).strip()
        exp_type = start_line.split(" ")[1]
        if exp_type == "IDLE":
            start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z')
        else:  # Stress test CPU consumption
            start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z') + timedelta(seconds=20)
        stop = datetime.strptime(stop_str, '%Y-%m-%d %H:%M:%S%z')
        timestamps.append((start, stop, exp_type))
    return timestamps


def remove_outliers(df, column, out_range):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - out_range * iqr
    upper_bound = q3 + out_range * iqr
    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df_filtered


def get_experiment_data(start_date, stop_date, all_vars, exp_type, out_range):
    ec_cpu_df = pd.DataFrame()
    for var in all_vars:
        if var != "exp_type":
            df = query_influxdb(var_query[var], start_date, stop_date)
            df = remove_outliers(df, "_value", out_range)
            df.rename(columns={'_value': var}, inplace=True)
            df = df[["_time", var]]
            if ec_cpu_df.empty:
                ec_cpu_df = df
            else:
                ec_cpu_df = pd.merge(ec_cpu_df, df, on='_time')

        else:
            ec_cpu_df[var] = exp_type
    ec_cpu_df.rename(columns={'_time': 'time'}, inplace=True)
    ec_cpu_df.dropna(inplace=True)
    return ec_cpu_df[all_vars + ["time"]]


def get_time_series(x_vars, timestamps, out_range, temp=False):
    experiment_dates = parse_timestamps(timestamps)
    all_vars = x_vars.copy()
    if not temp:
        all_vars.extend(["energy", "exp_type"])
    time_series = pd.DataFrame(columns=all_vars)
    for start_date, stop_date, exp_type in experiment_dates:
        if temp:
            exp_type = None
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        stop_str = stop_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        experiment_data = get_experiment_data(start_str, stop_str, all_vars, exp_type, out_range)
        time_series = pd.concat([time_series, experiment_data], ignore_index=True)
    return time_series


def get_idle_consumption(time_series):
    return time_series[time_series["exp_type"] == "IDLE"]["energy"].mean()


def get_stress_data(time_series):
    return time_series[time_series["exp_type"] != "IDLE"]


def get_formatted_vars(x_vars, data):
    x_values = []
    for i, var in enumerate(x_vars):
        x_values.append(data[var].values.reshape(-1, 1))
    x_stack = np.hstack(x_values)
    y = data["energy"].values.reshape(-1, 1)
    return x_stack, y
