import time

from cpu_power_seer import utils
from cpu_power_seer.logs.logger import log


def main():

    start = time.time()
    start_cpu = time.process_time()

    # Parse arguments
    utils.parse_arguments.run()

    # Get train data
    start_gather = time.time()
    train_timestamps, temp_series, time_series = utils.get_train_data.run()
    end_gather = time.time()

    # Plot time series
    utils.plot_train_data.run(temp_series, time_series)

    # Train model
    start_train = time.time()
    reg_model = utils.train_model.run(train_timestamps, time_series)
    end_train = time.time()

    # Test model
    start_test = time.time()
    utils.test_model.run(reg_model)
    end_test = time.time()

    end = time.time()
    end_cpu = time.process_time()

    # Execution times
    log(f"TRAIN DATA GATHERING EXECUTION TIME: {end_gather - start_gather}")
    log(f"MODEL TRAINING EXECUTION TIME: {end_train - start_train}")
    log(f"MODEL TESTING EXECUTION TIME: {end_test - start_test}")
    log(f"TOTAL CPU TIME: {end_cpu - start_cpu}")
    log(f"TOTAL EXECUTION TIME: {end - start}")


if __name__ == '__main__':
    main()

