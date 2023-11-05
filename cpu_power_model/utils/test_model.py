import os
import re

from cpu_power_model.config import config
from cpu_power_model.logs.logger import log
from cpu_power_model.data.process import parse_timestamps, get_time_series, get_formatted_vars
from cpu_power_model.data.plot import plot_time_series, plot_model, plot_results


def get_test_name(file):
    pattern = r'\/([^/]+)\.'
    occurrences = re.findall(pattern, file)
    return occurrences[-1]


def set_test_output(test_name):
    config.test_results_dir = f'{config.output_dir}/test/{test_name}'
    config.img_dir = f'{config.test_results_dir}/img'
    os.makedirs(config.test_results_dir, exist_ok=True)
    os.makedirs(config.img_dir, exist_ok=True)
    log(f"Test {test_name} output directory set to {config.test_results_dir}")


def get_test_data(model, file):
    log(f"Parsing test timestamps from {file}")
    test_timestamps = parse_timestamps(file)
    log("Getting model variables time series from corresponding period")
    test_time_series = get_time_series(config.x_vars + ["power"], test_timestamps, config.test_range)
    #plot_time_series("Test Time Series", test_time_series, config.x_vars, f'{config.model_name}-test-data.png')
    X_actual, y_actual = get_formatted_vars(config.x_vars, test_time_series)
    model.set_actual_values(X_actual, y_actual)
    return test_time_series


def save_model_results(model, test_time_series=None):

    expected = model.y_actual if model.y_actual is not None else model.y_test
    predicted = model.y_pred_actual if model.y_pred_actual is not None else model.y_pred
    plot_results(expected, predicted, f'{config.model_name}-results.png')
    # If actual test data is provided plot predicted time series
    if test_time_series is not None:
        predicted_col = predicted.flatten()
        test_time_series['power_predicted'] = predicted_col
        plot_time_series("Predicted Time Series", test_time_series,
                         config.x_vars, f'{config.model_name}-predictions.png', show_predictions=True)
    # If model dimension is 2 it is represented as a polynomial function
    if len(config.x_vars) == 1:
        plot_model(model, config.x_vars[0], f'{config.model_name}-function.png')
    model.write_performance(expected, predicted)


def run(model):
    if not len(config.test_ts_files_list) == 0:
        for file in config.test_ts_files_list:
            test_name = get_test_name(file)
            set_test_output(test_name)
            test_time_series = get_test_data(model, file)
            model.predict()
            save_model_results(model, test_time_series)
    else:
        model.predict()
        save_model_results(model)
