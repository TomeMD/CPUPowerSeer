from cpu_power_model.logs.logger import log
from cpu_power_model.config import config


def print_config():
    log(f"Model name: {config.model_name}")
    log(f"Testing Mode: {'Interactive' if config.interactive else 'Non-interactive'}")
    log(f"InfluxDB bucket name: {config.influxdb_bucket}")
    log(f"Train data timestamps file: {config.f_train_timestamps}")
    log(f"Actual (test) data timestamps file: {config.f_actual_timestamps}")
    log(f"Model variables: {config.x_vars}")
    log(f"Output directory: {config.output_dir}")
