import pandas as pd
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
        if (exp_type == "IDLE"):
            start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z')
        else: # Stress test CPU consumption
            start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z') + timedelta(seconds=20)
        stop = datetime.strptime(stop_str, '%Y-%m-%d %H:%M:%S%z')
        timestamps.append((start, stop, exp_type))
    return timestamps

def remove_outliers(df, column, range):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - range * IQR
    upper_bound = Q3 + range * IQR
    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df_filtered

def get_experiment_data(start_date, stop_date, exp_type, range):
    load_query
    load_df = query_influxdb(load_query, start_date, stop_date)
    freq_df = query_influxdb(freq_query, start_date, stop_date)
    energy_df = query_influxdb(energy_query, start_date, stop_date)
    load_df_filtered = remove_outliers(load_df, "_value", range)
    freq_df_filtered = remove_outliers(freq_df, "_value", range)
    energy_df_filtered = remove_outliers(energy_df, "_value", range)
    ec_cpu_df = pd.merge(load_df_filtered, energy_df_filtered, on="_time", suffixes=("_load", "_energy"))
    ec_cpu_df = pd.merge(ec_cpu_df, freq_df_filtered, on="_time", suffixes=("", "_freq"))
    ec_cpu_df.rename(columns={'_value': '_value_freq'}, inplace=True)
    ec_cpu_df = ec_cpu_df[["_time", "_value_load", "_value_freq", "_value_energy"]]
    ec_cpu_df["exp_type"] = exp_type
    ec_cpu_df.dropna(inplace=True)

    return ec_cpu_df

def get_time_series(experiment_dates, range):
    time_series = pd.DataFrame(columns=["_time", "_value_load", "_value_freq", "_value_energy", "exp_type"])
    for start_date, stop_date, exp_type in experiment_dates:
        experiment_data = get_experiment_data(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), stop_date.strftime("%Y-%m-%dT%H:%M:%SZ"), exp_type, range)
        time_series = pd.concat([time_series, experiment_data], ignore_index=True)
    return time_series