import warnings
from influxdb_client import InfluxDBClient
from influxdb_client.client.warnings import MissingPivotFunction
from urllib3.exceptions import ReadTimeoutError

from cpu_power_model.influxdb.influxdb_env import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG
from cpu_power_model.logs.logger import log

warnings.simplefilter("ignore", MissingPivotFunction)


def check_bucket_exists(bucket_name):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    buckets_api = client.buckets_api()
    if buckets_api.find_bucket_by_name(bucket_name) is None:
        log(f"Specified bucket {bucket_name} doesn't exists", "ERR")
        exit(1)


def query_influxdb(query, start_date, stop_date, bucket):
    retry = 3
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
    query = query.format(start_date=start_date, stop_date=stop_date, influxdb_bucket=bucket, influxdb_window="5s")
    while retry != 0:
        try:
            result = query_api.query_data_frame(query)
        except ReadTimeoutError:
            if retry != 0:
                log(f"InfluxDB query has timed out (start_date = {start_date}, stop_date = {stop_date}). Retrying", "WARN")
                retry -= 1
            else:
                log(f"InfluxDB query has timed out (start_date = {start_date}, stop_date = {stop_date}). No more tries", "ERR")
        except Exception as e:
            log(f"Unexpected error while querying InfluxDB (start_date = {start_date}, stop_date = {stop_date}).", "ERR")
            log(f"{e}", "ERR")
            exit(1)
        else:
            retry = 0

    return result
