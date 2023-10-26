from my_parser import create_parser, check_config, update_config
from run_test_mode import run_tests_with_mode
from cpu_power_model.config.print_config import print_config
from cpu_power_model.logs.logger import log
from cpu_power_model.config import config as conf
from cpu_power_model.process_data.process_data import *
from cpu_power_model.plot_data.plot_data import *
from cpu_power_model.model_energy.model_data import Model

if __name__ == '__main__':

    # Configuration
    parser = create_parser()
    args = parser.parse_args()
    update_config(args)
    check_config()
    print_config()

    # Get train data
    log(f"Parsing train timestamps from {conf.f_train_timestamps}")
    train_timestamps = parse_timestamps(conf.f_train_timestamps)
    log("Getting temperature time series from corresponding period")
    temp_series = get_time_series(["temp"], train_timestamps, conf.train_range, True)
    log("Getting model variables time series from corresponding period")
    time_series = get_time_series(conf.x_vars + ["energy"], train_timestamps, conf.train_range)

    # Plot time series
    plot_var("CPU Temperature", temp_series, "temp", f'{conf.model_name}-temperature-data.png')
    plot_time_series("Train Time Series", time_series, conf.x_vars, f'{conf.model_name}-train-data.png')

    # Prepare data
    idle_consumption = get_idle_consumption(train_timestamps, conf.train_range)
    X, y = get_formatted_vars(conf.x_vars, time_series)

    # Create model
    reg_model = Model(conf.model_name, idle_consumption, X, y)

    run_tests_with_mode(reg_model)


