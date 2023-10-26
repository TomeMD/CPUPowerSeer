import os
import argparse
from argparse import RawTextHelpFormatter

from cpu_power_model.logs.logger import log
from cpu_power_model.config import config
from cpu_power_model.influxdb.influxdb import check_bucket_exists


def create_parser():
    parser = argparse.ArgumentParser(
        description="Modeling CPU power consumption from InfluxDB time series.", formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive testing mode. When entering this mode CPU Power model will create the model and then ask to \
the user for test timestamps files to test \nthe model. Interactive mode will be \
useful to test one model with different test time series."
    )

    parser.add_argument(
        "-b",
        "--bucket",
        default="glances",
        help="InfluxDB Bucket to retrieve data from.",
    )

    parser.add_argument(
        "-t",
        "--train-timestamps",
        default="log/stress.timestamps",
        help="File storing time series timestamps from train data. By default is log/stress.timestamps. \
Timestamps must be stored in the following format:\n \
    <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-START>\n \
    <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-STOP>\n \
Example:\n \
    Spread_P&L STRESS-TEST (cores = 0,16) start: 2023-04-18 14:26:01+0000\n \
    Spread_P&L STRESS-TEST (cores = 0,16) stop: 2023-04-18 14:28:01+0000",
    )

    parser.add_argument(
        "-m",
        "--model-variables",
        default="load,freq",
        help="Comma-separated list of variables to use in the regression model.",
    )

    parser.add_argument(
        "-a",
        "--actual-timestamps",
        default=None,
        help="File storing time series timestamps from actual values of load and energy to \
test the model (in same format as train timestamps). \n\
If not specified train data will be split into train and test data.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="out",
        help="Directory to save time series plots and results. By default is './out'.",
    )

    parser.add_argument(
        "-n",
        "--name",
        default="EC-CPU-MODEL",
        help="Name of the model. It is useful to generate models from different sets of experiments \
in an orderly manner. By default is 'EC-CPU-MODEL'",
    )

    return parser


def check_x_vars():
    aux = set(config.x_vars) - set(config.supported_vars)
    if any(var not in config.supported_vars for var in config.x_vars):
        log(f"{aux} not supported. Supported vars: {config.supported_vars}", "ERR")
        exit(1)


def check_files():
    if not os.path.exists(config.f_train_timestamps):
        log(f"Specified non existent actual timestamps file: {config.f_train_timestamps}.", "ERR")
        exit(1)
    if config.actual and not os.path.exists(config.f_actual_timestamps):
        log(f"Specified non existent actual timestamps file: {config.f_actual_timestamps}.", "ERR")
        exit(1)


def check_config():
    check_x_vars()
    check_files()
    check_bucket_exists(config.influxdb_bucket)


def update_config(args):
    config.model_name = args.name
    config.verbose = args.verbose
    config.interactive = args.interactive
    config.influxdb_bucket = args.bucket
    config.f_train_timestamps = args.train_timestamps
    config.f_actual_timestamps = args.actual_timestamps
    config.actual = (config.f_actual_timestamps is not None)
    config.x_vars = args.model_variables.split(',')
    config.output_dir = args.output
    config.img_dir = f'{args.output}/img'
    config.log_file = f'{args.output}/{args.name}.log'
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.img_dir, exist_ok=True)

