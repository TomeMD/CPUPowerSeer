import argparse
from argparse import RawTextHelpFormatter

def create_parser():
    parser = argparse.ArgumentParser(description="Modeling CPU power consumption from InfluxDB time series.", formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "-t",
        "--train-timestamps",
        default="log/stress.timestamps",
        help="File storing time series timestamps from train data. By default is log/stress.timestamps. Timestamps must be stored in the following format:\n \
    <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-START>\n \
    <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-STOP>\n \
Example:\n \
    Spread_P&L STRESS-TEST (cores = 0,16) start: 2023-04-18 14:26:01+0000\n \
    Spread_P&L STRESS-TEST (cores = 0,16) stop: 2023-04-18 14:28:01+0000",
    )

    parser.add_argument(
        "-a",
        "--actual-timestamps",
        default=None,
        help="File storing time series timestamps from actual values of load and energy to test the model (in same format as train timestamps). If not \n \
        specified train data will be split into train and test data.",
    )

    parser.add_argument(
        "-tp",
        "--train-data-plot",
        default="img/train-data.png",
        help="Specifies the path to save the train data time series plot. By default is 'img/train-data.png'.",
    )

    parser.add_argument(
        "-ap",
        "--actual-data-plot",
        default="img/actual-data.png",
        help="Specifies the path to save the actual data time series plot. By default is 'img/actual-data.png'.",
    )

    parser.add_argument(
        "-n",
        "--name",
        default="EC-CPU-MODEL",
        help="Name of the model. It is useful to generate models from different sets of experiments in an orderly manner. By default is 'EC-CPU-MODEL'",
    )

    return parser
