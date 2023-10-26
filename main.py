from utils.my_parser import create_parser
from run_test_mode import run_tests_with_mode
from utils.process_data import *
from utils.plot_data import *
from utils.model_data import Model

if __name__ == '__main__':

    # Configuration
    parser = create_parser()
    args = parser.parse_args()
    config.set_config(args)
    config.check_args()
    config.print_header()
    config.print_config()

    # Get train data
    config.log(f"Parsing train timestamps from {config.f_train_timestamps}")
    train_timestamps = parse_timestamps(config.f_train_timestamps)
    config.log("Getting temperature time series from corresponding period")
    temp_series = get_time_series(["temp"], train_timestamps, config.train_range, True)
    config.log("Getting model variables time series from corresponding period")
    time_series = get_time_series(config.x_vars+["energy"], train_timestamps, config.train_range)

    # Plot time series
    plot_var("CPU Temperature", temp_series, "temp", f'{config.model_name}-temperature-data.png')
    plot_time_series("Train Time Series", time_series, config.x_vars, f'{config.model_name}-train-data.png')

    # Prepare data
    idle_consumption = get_idle_consumption(train_timestamps, config.train_range)
    X, y = get_formatted_vars(config.x_vars, time_series)

    # Create model
    reg_model = Model(config.model_name, idle_consumption, X, y)

    run_tests_with_mode(reg_model)


