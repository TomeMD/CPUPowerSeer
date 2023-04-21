import argparse
from argparse import RawTextHelpFormatter

def create_parser():
    parser = argparse.ArgumentParser(description="Modeling CPU power consumption from InfluxDB time series.", formatter_class=RawTextHelpFormatter)

    parser.add_argument(
        "-t",
        "--timestamps-file",
        default="log/stress.timestamps",
        help="File storing time series timestamps. By default is log/stress.timestamps. Timestamps must be stored in the following format:\n \
    <some-text-or-nothing> start: '%%Y-%%m-%%d %%H:%%M:%%S%%z'\n \
    <some-text-or-nothing> stop: '%%Y-%%m-%%d %%H:%%M:%%S%%z' \n \
Example:\n \
    Spread_P&L (cores = 0,16) start: 2023-04-18 14:26:01+0000\n \
    Spread_P&L (cores = 0,16) stop: 2023-04-18 14:28:01+0000",
    )

    parser.add_argument(
        "-r",
        "--regression-plot-path",
        default="img/regression.png",
        help="Specifies the path to save the regression plot. By default is 'img/regression.png'.",
    )

    parser.add_argument(
        "-d",
        "--data-plot-path",
        default="img/data.png",
        help="Specifies the path to save the data plot. By default is 'img/data.png'.",
    )

    return parser
