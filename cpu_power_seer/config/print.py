from cpu_power_seer.logs.logger import log
from cpu_power_seer.config import config


def print_config():
    log(f"Model name: {config.model_name}")
    log(f"Prediction method: {config.prediction_method}")
    log(f"InfluxDB bucket name: {config.influxdb_bucket}")
    log(f"Train data timestamps file: {config.train_ts_file}")
    log(f"Actual (test) data timestamps files list: {config.test_ts_files_list}")
    log(f"Model variables: {config.x_vars}")
    log(f"Output directory: {config.output_dir}")
