from cpu_power_model import utils


def main():

    # Parse arguments
    utils.parse_arguments.run()

    # Get train data
    train_timestamps, temp_series, time_series = utils.get_train_data.run()

    # Plot time series
    utils.plot_train_data.run(temp_series, time_series)

    # Train model
    reg_model = utils.train_model.run(train_timestamps, time_series)

    # Test model
    utils.run_test_mode.run(reg_model)


if __name__ == '__main__':
    main()

