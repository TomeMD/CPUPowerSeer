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
    temp_series = get_time_series(["temp"], config.f_train_timestamps, config.train_range, temp=True)
    time_series = get_time_series(config.x_vars, config.f_train_timestamps, config.train_range)

    # Plot time series
    plot_temperature(temp_series, f'{config.model_name}-temperature-data.png')
    plot_time_series(time_series, config.x_vars, f'{config.model_name}-train-data.png')

    # Prepare data
    idle_consumption = get_idle_consumption(time_series)
    stress_data = get_stress_data(time_series)
    X, y = get_formatted_vars(config.x_vars, stress_data)

    # Create model
    model = Model(config.model_name, idle_consumption, X, y)

    # Get actual test values if provided
    if config.f_actual_timestamps is not None:
        test_time_series = get_time_series(config.x_vars, config.f_actual_timestamps, config.test_range)
        plot_time_series(test_time_series, config.x_vars, f'{config.model_name}-test-data.png')
        X_actual, y_actual = get_formatted_vars(config.x_vars, test_time_series)
        model.update_test_values(X_actual, y_actual)

    # Predict values
    model.predict_values()

    # Get results
    plot_results(model.y_test, model.y_poly_pred, f'{config.img_dir}/{config.model_name}-results.png')
    model.write_model_performance()

