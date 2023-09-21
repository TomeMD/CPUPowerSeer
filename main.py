from utils.my_parser import create_parser
from utils.process_data import *
from utils.plot_data import *
from utils.model_data import Model


import warnings
from influxdb_client.client.warnings import MissingPivotFunction

if __name__ == '__main__':

    # Configuration
    parser = create_parser()
    args = parser.parse_args()
    config.set_config(args)
    warnings.simplefilter("ignore", MissingPivotFunction)

    # Get train data
    temp_series = get_time_series(["temp"], config.f_train_timestamps, config.train_range)
    energy_series = get_time_series(["energy", "exp_type"], config.f_train_timestamps, config.train_range)
    x_var_series = get_time_series(config.x_vars, config.f_train_timestamps, config.train_range)
    time_series = merge(x_var_series, energy_series, 'time')

    # Plot time series
    plot_temperature(temp_series, f'{config.model_name}-temperature-data.png')
    plot_time_series(time_series, config.x_vars, f'{config.model_name}-train-data.png')

    # Prepare data
    idle_consumption = get_idle_consumption(energy_series)
    stress_data = get_stress_data(time_series)
    X, y = get_formatted_vars(config.x_vars, stress_data)

    # Create model
    model = Model(config.model_name, idle_consumption, X, y)

    # Get actual test values if provided
    if config.actual:
        test_time_series = get_time_series(config.x_vars + ["energy", "exp_type"], config.f_actual_timestamps, config.test_range)
        plot_time_series(test_time_series, config.x_vars, f'{config.model_name}-test-data.png')
        X_actual, y_actual = get_formatted_vars(config.x_vars, test_time_series)
        model.set_actual_values(X_actual, y_actual)

    # Predict values
    model.predict()

    # Get results
    plot_results(model.y_test, model.y_pred, f'{config.img_dir}/{config.model_name}-results.png')
    # If model dimension is 2 it is represented as a function
    if len(config.x_vars) == 1:
        plot_model(model, config.x_vars[0], f'{config.img_dir}/{config.model_name}-function.png')
    model.write_model_performance(config.actual)

