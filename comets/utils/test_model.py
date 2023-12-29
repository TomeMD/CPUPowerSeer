import os
import re
import pandas as pd

from comets.config import config
from comets.logs.logger import log
from comets.data.process import get_timestamp_from_line, get_time_series, get_formatted_vars
from comets.data.plot import plot_time_series, plot_model, plot_results
from comets.data.model.utils import write_performance


def get_test_name(file):
    pattern = r'\/([^/]+)\.'
    occurrences = re.findall(pattern, file)
    return occurrences[-1]


def get_threads_timestamps(file):
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        log(f"Error while parsing timestamps (file doesn't exists): {file}", "ERR")
        return []
    threads_timestamps = []
    for i in range(0, len(lines), 2):
        start_line = lines[i]
        stop_line = lines[i+1]
        threads = len(start_line.split(" ")[-4][:-1].split(","))
        threads_timestamps.append((threads, start_line, stop_line))
    return threads_timestamps


def set_test_output(test_name, threads):
    config.test_results_dir = f'{config.test_dir}/{test_name}/{threads}' if threads != 0 \
        else f'{config.test_dir}/{test_name}'
    config.img_dir = f'{config.test_results_dir}/img'
    os.makedirs(config.test_results_dir, exist_ok=True)
    os.makedirs(config.img_dir, exist_ok=True)
    log(f"Test {test_name} output directory set to {config.test_results_dir}")


def get_test_data(start_line, stop_line, initial_date):
    test_timestamps = get_timestamp_from_line(start_line, stop_line, 0)
    log("Getting model variables time series from corresponding period")
    time_series = get_time_series(config.x_vars + ["power"], test_timestamps, config.test_range, initial_date=initial_date)
    return time_series
    # plot_time_series("Test Time Series", test_time_series, config.x_vars, f'{config.model_name}-test-data.png')


def update_test_model_values(model, time_series):
    X_actual, y_actual = get_formatted_vars(config.x_vars, time_series)
    model.set_actual_values(X_actual, y_actual)


def save_model_results(model, threads, test_name, test_time_series=None):

    expected = model.y_actual if model.y_actual is not None else model.y_test
    predicted = model.y_pred_actual if model.y_pred_actual is not None else model.y_pred
    plot_results(expected, predicted, f'{config.model_name}-results.png')

    # If writing test results with all threads write also to common R2 file
    write_performance(model.name, expected, predicted,
                      equation=model.equation, write_common_file=(threads == 0), test_name=test_name)

    # If actual test data is provided plot predicted time series
    if test_time_series is not None:
        test_time_series['power_predicted'] = model.y_pred_actual.flatten()
        plot_time_series("Predicted Time Series", test_time_series,
                         config.x_vars, f'{config.model_name}-predictions.png', show_predictions=True)

    # If model dimension is 2 it is represented as a polynomial function
    if len(config.x_vars) == 1:
        plot_model(model, config.x_vars[0], f'{config.model_name}-function.png')


def run_test(model, threads, test_name, time_series):
    set_test_output(test_name, threads)
    update_test_model_values(model, time_series)
    model.test()
    save_model_results(model, threads, test_name, time_series)


def fix_time_units(df, current, prev):
    if current == "hours" and prev == "seconds":
        df["time_diff"] = df["time_diff"] / 3600
    else:
        df["time_diff"] = df["time_diff"] / 60
    df["time_unit"] = current
    log(f"Test time series time units have been modified from {prev} to {current}", "WARN")
    return df


def run(model):
    if config.test_ts_files_list is not None:
        for file in config.test_ts_files_list:
            test_name = get_test_name(file)
            threads_timestamps = get_threads_timestamps(file)
            test_time_series = pd.DataFrame(columns=config.x_vars.copy() + ["power"] + ["time_diff"] + ["time_unit"])
            first = True
            initial_date = None
            prev_time_unit = None
            for t in threads_timestamps:
                log(f"Running test {test_name} with {t[0]} threads")
                time_series_threads = get_test_data(t[1], t[2], initial_date)
                current_time_unit = time_series_threads["time_unit"].iloc[0]
                if first:
                    prev_time_unit = current_time_unit
                    initial_date = time_series_threads["time"].min()
                    first = False
                if current_time_unit != prev_time_unit:
                    test_time_series = fix_time_units(test_time_series, current_time_unit, prev_time_unit)
                    prev_time_unit = current_time_unit
                run_test(model, t[0], test_name, time_series_threads)
                test_time_series = pd.concat([test_time_series, time_series_threads], ignore_index=True)
            run_test(model, 0, test_name, test_time_series)
    else:
        set_test_output("test_split", 0)
        model.test()
        save_model_results(model, 0, "Test Split")
