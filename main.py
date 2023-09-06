from utils.my_parser import create_parser
from utils.process_data import parse_timestamps, get_experiment_data, get_time_series
from utils.plot_data import plot_time_series, plot_model
from utils.model_data import Model

import numpy as np
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

if __name__ == '__main__':
 
    parser = create_parser()
    args = parser.parse_args()
    f_train_timestamps = args.train_timestamps
    f_actual_timestamps = args.actual_timestamps
    model_name = args.name
    train_data_plot = args.train_data_plot
    actual_data_plot = args.actual_data_plot
    train_range = 1.5
    test_range = 1.5  # 0.001

    warnings.simplefilter("ignore", MissingPivotFunction)

    # Get train data
    experiment_dates = parse_timestamps(f_train_timestamps) # Get timestamps from log file
    time_series = get_time_series(experiment_dates, train_range)

    # Plot time series
    plot_time_series(time_series, "Series temporales",
                     "Tiempo (HH:MM)", ["Utilización de CPU (%)", "Frecuencia de CPU (MHz)", "Consumo energético (J)"], train_data_plot)
    idle_consumption = time_series[time_series["exp_type"] == "IDLE"]["_value_energy"].mean()
    
    # Prepare data
    stress_data = time_series[time_series["exp_type"] != "IDLE"]
    X1 = stress_data["_value_load"].values.reshape(-1, 1)
    X2 = stress_data["_value_freq"].values.reshape(-1, 1)
    X = np.hstack((X1, X2))
    y = stress_data["_value_energy"].values.reshape(-1, 1)

    # Create model and predict values
    model = Model(model_name, idle_consumption, X, y)
    model.predict_values()

    # Get actual values if provided
    X_actual = y_actual = None
    if f_actual_timestamps is not None:
        test_dates = parse_timestamps(f_actual_timestamps)
        test_time_series = get_time_series(test_dates, test_range)
        plot_time_series(test_time_series, "Series temporales",
                         "Tiempo (HH:MM)", ["Utilización de CPU (%)", "Frecuencia de CPU (MHz)", "Consumo energético (J)"], actual_data_plot)
        X1_actual = test_time_series["_value_load"].values.reshape(-1, 1)
        X2_actual = test_time_series["_value_freq"].values.reshape(-1, 1)
        X_actual = np.hstack((X1_actual, X2_actual))
        y_actual = test_time_series["_value_energy"].values.reshape(-1, 1)
        model.update_test_values(X_actual, y_actual)
        model.predict_values()

    model.show_model_performance()

