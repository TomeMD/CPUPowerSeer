from my_parser import create_parser
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
from datetime import datetime, timedelta
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

degree = 2

load_query = '''
    from(bucket: "{influxdb_bucket}") 
        |> range(start: {start_date}, stop: {stop_date}) 
        |> filter(fn: (r) => r["_measurement"] == "percpu")
        |> filter(fn: (r) => r["_field"] == "user" )
        |> aggregateWindow(every: 2s, fn: mean, createEmpty: false)
        |> group(columns: ["_measurement"])  
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)
        |> yield(name: "sum")'''

energy_query = '''
    from(bucket: "{influxdb_bucket}") 
        |> range(start: {start_date}, stop: {stop_date}) 
        |> filter(fn: (r) => r["_measurement"] == "ENERGY_PP0")
        |> filter(fn: (r) => r["_field"] == "rapl:::PP0_ENERGY:PACKAGE0(J)" or r["_field"] == "rapl:::PP0_ENERGY:PACKAGE1(J)")
        |> aggregateWindow(every: 2s, fn: sum, createEmpty: false)
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> map(fn: (r) => ({{
            _time: r._time, 
            host: r.host, 
            _measurement: r._measurement, 
            _field: "total_energy", 
            _value: r["rapl:::PP0_ENERGY:PACKAGE0(J)"] + r["rapl:::PP0_ENERGY:PACKAGE1(J)"]
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
        print(start_str, stop_str)
        start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z') + timedelta(seconds=10)
        stop = datetime.strptime(stop_str, '%Y-%m-%d %H:%M:%S%z') - timedelta(seconds=10)

        timestamps.append((start, stop))
    return timestamps

def query_influxdb(query, start_date, stop_date):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    query_api = client.query_api()
    query = query.format(start_date=start_date, stop_date=stop_date, influxdb_bucket=influxdb_bucket)
    result = query_api.query_data_frame(query)
    return result

def get_experiment_data(start_date, stop_date):
    load_df = query_influxdb(load_query, start_date, stop_date)
    energy_df = query_influxdb(energy_query, start_date, stop_date)
    print(load_df)
    ec_cpu_df = pd.merge(load_df, energy_df, on="_time", suffixes=("_load", "_energy"))
    ec_cpu_df = ec_cpu_df[["_time", "_value_load", "_value_energy"]]
    ec_cpu_df.dropna(inplace=True)

    return ec_cpu_df

def plot_time_series(df, title, xlabel, ylabel, path):
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
    plt.savefig(path)
    #plt.show(block=False)

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
    
    parser = create_parser()
    args = parser.parse_args()

    timestamps_file = args.timestamps_file
    regression_plot_path = args.regression_plot_path
    data_plot_path = args.data_plot_path

    # Get timestamps from log file
    experiment_dates = parse_timestamps(timestamps_file)
    
    warnings.simplefilter("ignore", MissingPivotFunction)
    # Get and transform data
    ec_cpu_df = pd.DataFrame(columns=["_time", "_value_load", "_value_energy"])
    for start_date, stop_date in experiment_dates:
        experiment_data = get_experiment_data(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), stop_date.strftime("%Y-%m-%dT%H:%M:%SZ"))
        ec_cpu_df = pd.concat([ec_cpu_df, experiment_data], ignore_index=True)

    # Plot data
    plot_time_series(ec_cpu_df, "Utilización de CPU y consumo energético", "Tiempo (HH:MM)", "Utilización (%) y energía (J)", data_plot_path)

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
    plt.tight_layout()
    plt.savefig(regression_plot_path)
    #plt.show()