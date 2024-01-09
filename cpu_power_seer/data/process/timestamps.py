from datetime import datetime, timedelta

from cpu_power_seer.logs.logger import log


def get_timestamp_from_line(start_line, stop_line, offset):
    start_str = " ".join(start_line.split(" ")[-2:]).strip()
    stop_str = " ".join(stop_line.split(" ")[-2:]).strip()
    exp_type = start_line.split(" ")[1]
    if exp_type == "IDLE":
        offset = 0
    start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S%z') + timedelta(seconds=offset)
    stop = datetime.strptime(stop_str, '%Y-%m-%d %H:%M:%S%z') - timedelta(seconds=offset)
    return [(start, stop, exp_type)]


def parse_timestamps(file):
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        log(f"Error while parsing timestamps (file doesn't exists): {file}", "ERR")
    timestamps = []
    for i in range(0, len(lines), 2):
        start_line = lines[i]
        stop_line = lines[i + 1]
        ts_line = get_timestamp_from_line(start_line, stop_line, 20)
        timestamps.append(ts_line[0])
    log(f"Timestamps belong to period [{timestamps[0][0]}, {timestamps[-1][1]}]")
    return timestamps


def get_threads_timestamps(file):
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        log(f"Error while parsing timestamps (file doesn't exists): {file}", "ERR")
        return []
    threads_timestamps = []
    for i in range(0, len(lines), 2):
        start_line = lines[i]
        stop_line = lines[i+1]
        threads = len(start_line.split(" ")[-4][:-1].split(","))
        threads_timestamps.append((threads, start_line, stop_line))
    return threads_timestamps
