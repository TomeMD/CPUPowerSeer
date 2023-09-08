import utils.config as config
from utils.my_parser import create_parser
from utils.process_data import parse_timestamps, get_time_series
from utils.plot_data import plot_time_series
from utils.model_data import Model

import numpy as np
import os
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

if __name__ == '__main__':
 
    parser = create_parser()
    args = parser.parse_args()
    config.f_train_timestamps = args.train_timestamps
    config.f_actual_timestamps = args.actual_timestamps
    config.model_name = args.name
    config.output_dir = args.output
    config.img_dir = f'{config.output_dir}/img'
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.img_dir, exist_ok=True)
    warnings.simplefilter("ignore", MissingPivotFunction)

    # Get train data
    experiment_dates = parse_timestamps(config.f_train_timestamps)  # Get timestamps from log file
    time_series = get_time_series(experiment_dates, config.train_range)

    # Plot time series
    plot_time_series(time_series, "Series temporales", "Tiempo (HH:MM)",
                     ["Utilización de CPU (%)", "Frecuencia de CPU (MHz)", "Consumo energético (J)"],
                     f'{config.model_name}-train-data.png')
    idle_consumption = time_series[time_series["exp_type"] == "IDLE"]["_value_energy"].mean()
    
    # Prepare data
    stress_data = time_series[time_series["exp_type"] != "IDLE"]
    X1 = stress_data["_value_load"].values.reshape(-1, 1)
    X2 = stress_data["_value_freq"].values.reshape(-1, 1)
    X = np.hstack((X1, X2))
    y = stress_data["_value_energy"].values.reshape(-1, 1)

    # Create model and predict values
    model = Model(config.model_name, idle_consumption, X, y)
    model.predict_values()

    # Get actual values if provided
    X_actual = y_actual = None
    if config.f_actual_timestamps is not None:
        test_dates = parse_timestamps(config.f_actual_timestamps)
        test_time_series = get_time_series(test_dates, config.test_range)
        plot_time_series(test_time_series, "Series temporales", "Tiempo (HH:MM)",
                         ["Utilización de CPU (%)", "Frecuencia de CPU (MHz)", "Consumo energético (J)"],
                         f'{config.model_name}-test-data.png')
        X1_actual = test_time_series["_value_load"].values.reshape(-1, 1)
        X2_actual = test_time_series["_value_freq"].values.reshape(-1, 1)
        X_actual = np.hstack((X1_actual, X2_actual))
        y_actual = test_time_series["_value_energy"].values.reshape(-1, 1)
        model.update_test_values(X_actual, y_actual)
        model.predict_values()

    model.write_model_performance()

