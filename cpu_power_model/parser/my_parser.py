import os
import argparse
from argparse import RawTextHelpFormatter

from cpu_power_model.logs.logger import log
from cpu_power_model.config import config
from cpu_power_model.influxdb.influxdb import check_bucket_exists


def create_parser():
    parser = argparse.ArgumentParser(
        description="Modeling CPU Power consumption from InfluxDB time series.", formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase output verbosity",
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
        default="",
        help="File storing time series timestamps from train data. \
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
        help="Comma-separated list of variables to use in the regression model. Commonly known as predictor variables.",
    )

    parser.add_argument(
        "-a",
        "--actual-timestamps-list",
        default=None,
        help="Comma-separated list of files storing time series timestamps from actual values of predictor variables \
and power to test\nthe model (in same format as train timestamps). If any file is specified train data will be split \
into train and test data.",
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
        default="General",
        help="Name of the model. It is useful to generate models from different sets of experiments \
in an orderly manner. By default is 'General'",
    )

    return parser


def check_x_vars():
    aux = set(config.x_vars) - set(config.supported_vars)
    if any(var not in config.supported_vars for var in config.x_vars):
        log(f"{aux} not supported. Supported vars: {config.supported_vars}", "ERR")
        exit(1)


def check_files():
    if not os.path.exists(config.train_ts_file):
        log(f"Specified non existent train timestamps file: {config.train_ts_file}.", "ERR")
        exit(1)
    for file in config.test_ts_files_list:
        if not os.path.exists(file):
            log(f"Specified non existent file in actual timestamps files list: {file}.", "ERR")
            exit(1)


def check_config():
    check_x_vars()
    check_files()
    check_bucket_exists(config.influxdb_bucket)


def update_config(args):
    config.model_name = args.name
    config.verbose = args.verbose
    config.influxdb_bucket = args.bucket
    config.train_ts_file = args.train_timestamps
    config.test_ts_files_list = args.actual_timestamps_list.split(',')
    config.x_vars = args.model_variables.split(',')
    config.output_dir = args.output
    config.train_dir = f'{args.output}/train'
    config.test_dir = f'{args.output}/test'
    config.log_file = f'{args.output}/cpu_power_model.log'
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.train_dir, exist_ok=True)
    os.makedirs(config.test_dir, exist_ok=True)
