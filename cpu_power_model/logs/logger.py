import datetime
from termcolor import colored

from cpu_power_model.config import config


def print_header():
    print("CPU POWER MODEL")
    print("Modeling CPU Power Consumption from InfluxDB Time Series")


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

    with open(config.log_file, 'a') as f:
        f.write(log_entry)
    if print_log:
        print(f"{header} {message}")
