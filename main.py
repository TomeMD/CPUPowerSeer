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
from sklearn.preprocessing import PolynomialFeatures
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

degree = 2

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

def show_model_performance(name, expected, predicted):
    print(f"Modelo: {name}")
    print(f"Mean squared error: {mean_squared_error(expected, predicted)}")
    print(f"R2 score: {r2_score(expected, predicted)}")
    print("")

def plot_lin_regression(model, X, y):
    plt.plot(X, y, color="blue", linewidth=2, label="Regresión lineal")
    m = model.coef_[0]  # Coefficient (slope)
    b = model.intercept_  # Intercept (constant)
    return f"y = {b[0]:.4f} + {m[0]:.4f}x\n"

def plot_poly_regression(model, X, y):
    X_idx = X[:, 1].argsort()
    X_sorted = X[X_idx]
    y_sorted = y[X_idx]
    plt.plot(X_sorted[:, 1], y_sorted, color="red", linewidth=2, label="Regresión polinómica")
    m = model.coef_
    b = model.intercept_ 
    eq = f"y = {b[0]:.4f}"
    for i, c in enumerate(m[0][1:]):
        eq += f" + {c:.4f}x^{i+1}"
    eq+= "\n"
    return eq

if __name__ == '__main__':

    # Get data from InfluxDB
    warnings.simplefilter("ignore", MissingPivotFunction)
    load_df = query_influxdb(load_query)
    energy_df = query_influxdb(energy_query)

    # Transform and plot data
    ec_cpu_df = pd.merge(load_df, energy_df, on="_time", suffixes=("_load", "_energy"))
    ec_cpu_df = ec_cpu_df[["_time", "_value_load", "_value_energy"]]
    ec_cpu_df.dropna(inplace=True)

    plot_time_series(ec_cpu_df, "Utilización de CPU y consumo energético", "Tiempo (HH:MM)", "Utilización (%) y energía (J)")

    # Prepare model data
    X = ec_cpu_df["_value_load"].values.reshape(-1, 1)
    y = ec_cpu_df["_value_energy"].values.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    poly_features = PolynomialFeatures(degree=degree)
    X_poly_train = poly_features.fit_transform(X_train)
    X_poly_test = poly_features.transform(X_test)

    # Train models
    poly_reg = LinearRegression()
    lin_reg = LinearRegression()
    poly_reg.fit(X_poly_train, y_train)
    lin_reg.fit(X_train, y_train)

    # Test models
    y_poly_pred = poly_reg.predict(X_poly_test)
    y_pred = lin_reg.predict(X_test)

    # Show models performance
    show_model_performance("Regresión lineal", y_test, y_pred)
    show_model_performance("Regresión polinómica", y_test, y_poly_pred)

    # Plot results
    plt.figure()
    plt.scatter(X, y, color="grey", label="Datos")
    title = ""
    title += plot_lin_regression(lin_reg, X_test, y_pred)
    title += plot_poly_regression(poly_reg, X_poly_test, y_poly_pred)
    plt.title(title)
    plt.xlabel("Utilización de CPU")
    plt.ylabel("Consumo energético")
    plt.legend()
    plt.show()
