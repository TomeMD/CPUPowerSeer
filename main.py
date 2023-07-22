from utils.my_parser import create_parser
from utils.process_data import parse_timestamps, get_experiment_data, get_time_series
from utils.plot_data import plot_time_series, plot_model

import numpy as np
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def get_model_equation(model, idle_consumption):
    eq_lines = [
        f"y = {model.intercept_[0]:.0f}",
        *(
            f" + {model.coef_[0][i+1]:.8f}*{name}"
            for i, name in enumerate(["U_cpu", "F_cpu", "U_cpu^2", "(U_cpu*F_cpu)", "F_cpu^2"])
        ),
        f"\nConsumo en reposo: {idle_consumption:.0f} J"
    ]
    return "\n".join(eq_lines)

def show_model_performance(name, equation, expected, predicted):
    print(f"Modelo: {name}")
    print(f"Ecuación: {equation}")
    print(f"Mean squared error: {mean_squared_error(expected, predicted)}")
    print(f"R2 score: {r2_score(expected, predicted)}")
    print("")

if __name__ == '__main__':
 
    parser = create_parser()
    args = parser.parse_args()
    f_train_timestamps = args.train_timestamps
    f_actual_values = args.actual_values
    model_name = args.name
    regression_plot_path = args.regression_plot_path
    data_plot_path = args.data_plot_path

    warnings.simplefilter("ignore", MissingPivotFunction)

    # Get train data
    experiment_dates = parse_timestamps(f_train_timestamps) # Get timestamps from log file
    time_series = get_time_series(experiment_dates)

    # Plot time series
    plot_time_series(time_series, "Series temporales",
                     "Tiempo (HH:MM)", ["Utilización de CPU (%)", "Frecuencia de CPU (MHz)", "Consumo energético (J)"], data_plot_path)
    
    idle_consumption = time_series[time_series["exp_type"] == "IDLE"]["_value_energy"].mean()
    
    # Split into train and test data
    stress_data = time_series[time_series["exp_type"] != "IDLE"]
    X1 = stress_data["_value_load"].values.reshape(-1, 1)
    X2 = stress_data["_value_freq"].values.reshape(-1, 1)
    X = np.hstack((X1, X2))
    y = stress_data["_value_energy"].values.reshape(-1, 1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


    poly_features = PolynomialFeatures(degree=2)
    X_poly_train = poly_features.fit_transform(X_train)
    X_poly_test = poly_features.transform(X_test)

    # Train model
    poly_reg = LinearRegression()
    poly_reg.fit(X_poly_train, y_train)
    equation = get_model_equation(poly_reg, idle_consumption)

    # Get predicted values
    y_poly_pred = poly_reg.predict(X_poly_test)

    # Get actual values if provided
    X_actual = y_actual = None
    if f_actual_values is not None:
        test_dates = parse_timestamps(f_actual_values)
        test_df = get_time_series(test_dates)
        X1_actual = test_df["_value_load"].values.reshape(-1, 1)
        X2_actual = test_df["_value_load"].values.reshape(-1, 1)
        X_actual = np.hstack((X1_actual, X2_actual))
        y_actual = test_df["_value_energy"].values.reshape(-1, 1)

    # Plot model
    plot_model(poly_reg, (X_actual, y_actual), X_poly_test, y_poly_pred, regression_plot_path)

    # If actual values are provided they are used to test the model
    if (X_actual is not None and y_actual is not None):
        y_test = y_actual
        X_poly_actual = poly_features.transform(X_actual)
        y_poly_pred = poly_reg.predict(X_poly_actual)

    show_model_performance(f"{model_name} (Regresión polinómica)", equation, y_test, y_poly_pred)

