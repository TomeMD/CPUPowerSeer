import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from datetime import datetime
from influxdb_client import InfluxDBClient
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from matplotlib.dates import DateFormatter, MinuteLocator
from influxdb_client.client.warnings import MissingPivotFunction

influxdb_url = "http://montoxo.des.udc.es:8086"
influxdb_token = "MyToken"
influxdb_org = "MyOrg"
influxdb_bucket = "glances"

start_date = datetime(2023, 4, 4, 8, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")
stop_date = datetime(2023, 4, 4, 9, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")

load_query = f'''
    from(bucket: "{influxdb_bucket}") 
        |> range(start: {start_date}, stop: {stop_date}) 
        |> filter(fn: (r) => r["_measurement"] == "percpu") 
        |> filter(fn: (r) => r["_field"] == "user") 
        |> group(columns: ["_measurement"]) 
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false) 
        |> yield(name: "sum")'''

energy_query = f'''
    from(bucket: "{influxdb_bucket}") 
        |> range(start: {start_date}, stop: {stop_date}) 
        |> filter(fn: (r) => r["_measurement"] == "ENERGY_PP0") 
        |> filter(fn: (r) => r["_field"] == "rapl:::PP0_ENERGY:PACKAGE0(J)" or r["_field"] == "rapl:::PP0_ENERGY:PACKAGE1(J)") 
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false) 
        |> group(columns: ["_measurement"]) 
        |> yield(name: "mean")'''

def query_influxdb(query):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    query_api = client.query_api()
    result = query_api.query_data_frame(query)
    return result

def plot_time_series(df, title, xlabel, ylabel):
    plt.figure()
    sns.lineplot(x=df["_time"],y=df["_value_load"], label="Utilización de CPU")
    sns.lineplot(x=df["_time"],y=df["_value_energy"], label="Consumo energético")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    ax = plt.gca()
    ax.xaxis.set_major_locator(MinuteLocator(interval=10))
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show(block=False)

if __name__ == '__main__':

    warnings.simplefilter("ignore", MissingPivotFunction)
    load_df = query_influxdb(load_query)
    energy_df = query_influxdb(energy_query)

    ec_cpu_df = pd.merge(load_df, energy_df, on="_time", suffixes=("_load", "_energy"))
    ec_cpu_df = ec_cpu_df[["_time", "_value_load", "_value_energy"]]
    ec_cpu_df.dropna(inplace=True)

    plot_time_series(ec_cpu_df, "Utilización de CPU y consumo energético", "Tiempo (HH:MM)", "Utilización (%) y energía (J)")

    X = ec_cpu_df["_value_load"].values.reshape(-1, 1)
    y = ec_cpu_df["_value_energy"].values.reshape(-1, 1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    log_reg = LinearRegression()
    log_reg.fit(X_train, y_train)

    y_pred = log_reg.predict(X_test)

    for cpu, power_pred, power in zip(X_test, y_pred, y_test):
        print(f"Utilización de CPU: {cpu} - Consumo predicho: {power_pred} - Consumo real: {power}")

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("Mean squared error: ", mse)
    print("R2 score: ", r2)

    plt.figure()
    plt.scatter(X, y, color="grey", label="Datos")
    plt.plot(X_test, y_pred, color="blue", linewidth=2, label="Regresión lineal")
    plt.xlabel("Utilización de CPU")
    plt.ylabel("Consumo energético")
    plt.legend()
    plt.show()
