# CPU Utilization VS Power Consumption

This tool builds a model to predict CPU energy consumption from CPU utilization using InfluxDB time series.

## Requirements

You need to install the following libraries:

```python
pip install influxdb-client pandas numpy scikit-learn matplotlib
```

## Configuration

Before using this tool you must configure the InfluxDB server from which the metrics will be exported, as well as the timestamps of the time series you want to obtain from that server.

### InfluxDB server

To modify your InfluxDB server simply modify the following code variables:

```python
influxdb_url = "influxdb-server:port"
influxdb_token = "your-token"
influxdb_org = "your-org"
influxdb_bucket = "your-bucket"
```

It is assumed that this server stores Glances and RAPL metrics in a proper format.

### Timestamps

To use the tool you must add your test timestamps (UTC) in the following format:

```shell
<test_name> (<load>) <start | stop>: <timestamp>
```

Another option is to hardcode these timestamps by modifying the code. For example, to hardcode the metrics collection for April 15, 2023 between 15:28:06 and 15:51:30, the following code could be used:

```python
# Get timestamps from log file
#experiment_dates = parse_timestamps(log_file)

experiment_dates = [(datetime(2023, 4, 15, 15, 28, 6), datetime(2023, 4, 15, 15, 51, 30))]
```







