import datetime
from termcolor import colored

import utils.config


def print_header():
    print("CPU POWER MODEL")
    print("Modeling CPU Energy Consumption from InfluxDB Time Series")


def get_formatted_input(message):
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    header = colored(f"[{timestamp} INPUT]", "white", "on_blue")
    return f"{header} {message}"


def get_input_and_log(message):
    formatted_msg = get_formatted_input(message)
    input_msg = input(formatted_msg)
    log(f"{message} {input_msg}", print_log=False)
    return input_msg


def log(message, message_type="INFO", print_log=True):
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    header_colors = {
        "INFO": ("white", "on_green"),
        "WARN": ("white", "on_yellow"),
        "ERR": ("white", "on_red"),
    }
    color, on_color = header_colors.get(message_type)
    header = colored(f"[{timestamp} {message_type}]", color, on_color)
    log_entry = f"[{timestamp} {message_type}] {message}\n"

    with open(utils.config.log_file, 'a') as f:
        f.write(log_entry)
    if print_log:
        print(f"{header} {message}")
