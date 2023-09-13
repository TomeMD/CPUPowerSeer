import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.influxdb import query_influxdb

load_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "total" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)'''

freq_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "cpu_frequency")
        |> filter(fn: (r) => r["_field"] == "value" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)'''

energy_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "ENERGY_PACKAGE")
        |> filter(fn: (r) => r["_field"] == "rapl:::PACKAGE_ENERGY:PACKAGE0(J)" or r["_field"] == "rapl:::PACKAGE_ENERGY:PACKAGE1(J)")
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> map(fn: (r) => ({{
            _time: r._time,
            host: r.host,
            _measurement: r._measurement,
            _field: "total_energy",
            _value: (if exists r["rapl:::PACKAGE_ENERGY:PACKAGE0(J)"] then r["rapl:::PACKAGE_ENERGY:PACKAGE0(J)"] else 0.0)
                  + (if exists r["rapl:::PACKAGE_ENERGY:PACKAGE1(J)"] then r["rapl:::PACKAGE_ENERGY:PACKAGE1(J)"] else 0.0)
        }}))'''

temp_query = '''
    from(bucket: "{influxdb_bucket}")
        |> range(start: {start_date}, stop: {stop_date})
        |> filter(fn: (r) => r["_measurement"] == "sensors")
        |> filter(fn: (r) => r["_field"] == "value")
        |> filter(fn: (r) => r["label"] == "Package id 0" or r["label"] == "Package id 1")
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["label"], valueColumn: "_value")
        |> map(fn: (r) => ({{
            _time: r._time,
            _value: (if exists r["Package id 0"] then r["Package id 0"] else 0.0) 
                  + (if exists r["Package id 1"] then r["Package id 1"] else 0.0)
        }}))
'''


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

def get_temp_data(start_date, stop_date):
    temp_df = query_influxdb(temp_query, start_date, stop_date)
    temp_df.rename(columns={'_value': 'temp'}, inplace=True)
    temp_df.rename(columns={'_time': 'time'}, inplace=True)
    temp_df = temp_df[["time", "temp"]]
    temp_df.dropna(inplace=True)
    return temp_df
def get_experiment_data(start_date, stop_date, exp_type, out_range):
    load_df = query_influxdb(load_query, start_date, stop_date)
    freq_df = query_influxdb(freq_query, start_date, stop_date)
    energy_df = query_influxdb(energy_query, start_date, stop_date)
    load_df_filtered = remove_outliers(load_df, "_value", out_range)
    freq_df_filtered = remove_outliers(freq_df, "_value", out_range)
    energy_df_filtered = remove_outliers(energy_df, "_value", out_range)
    ec_cpu_df = pd.merge(load_df_filtered, energy_df_filtered, on="_time", suffixes=("_load", "_energy"))
    ec_cpu_df.rename(columns={'_value_load': 'load'}, inplace=True)
    ec_cpu_df.rename(columns={'_value_energy': 'energy'}, inplace=True)
    ec_cpu_df = pd.merge(ec_cpu_df, freq_df_filtered, on="_time", suffixes=("", "_freq"))
    ec_cpu_df.rename(columns={'_value': 'freq'}, inplace=True)
    ec_cpu_df.rename(columns={'_time': 'time'}, inplace=True)
    ec_cpu_df = ec_cpu_df[["time", "load", "freq", "energy"]]
    ec_cpu_df["exp_type"] = exp_type
    ec_cpu_df.dropna(inplace=True)
    return ec_cpu_df


def get_temp_series(timestamps):
    experiment_dates = parse_timestamps(timestamps)
    temp_series = pd.DataFrame(columns=["time", "temp"])
    for start_date, stop_date, _ in experiment_dates:
        temp_data = get_temp_data(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), stop_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        temp_series = pd.concat([temp_series, temp_data], ignore_index=True)
    return temp_series


def get_time_series(timestamps, out_range):
    experiment_dates = parse_timestamps(timestamps)
    time_series = pd.DataFrame(columns=["time", "load", "freq", "energy", "exp_type"])
    for start_date, stop_date, exp_type in experiment_dates:
        experiment_data = get_experiment_data(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), stop_date.strftime("%Y-%m-%dT%H:%M:%SZ"), exp_type, out_range)
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
