# CPU Power Consumption Modeling

This tool builds a model to predict CPU energy consumption from different CPU variables (Utilization, Frequency,...) using InfluxDB time series.

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

## Installation

To install and use this tool run:

```
pip install .
```

If you only want to install the project dependencies, run:

```
pip install -r requirements.txt
```

## Execution and options

```shell
usage: cpu-power-model [-h] [-v] [-b BUCKET] [-t TRAIN_TIMESTAMPS] [-m MODEL_VARIABLES] [-a ACTUAL_TIMESTAMPS_LIST] [-o OUTPUT] [-n NAME]

Modeling CPU power consumption from InfluxDB time series.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -b BUCKET, --bucket BUCKET
                        InfluxDB Bucket to retrieve data from.
  -t TRAIN_TIMESTAMPS, --train-timestamps TRAIN_TIMESTAMPS
                        File storing time series timestamps from train data. Timestamps must be stored in the following format:
                             <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-START>
                             <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-STOP>
                         Example:
                             Spread_P&L STRESS-TEST (cores = 0,16) start: 2023-04-18 14:26:01+0000
                             Spread_P&L STRESS-TEST (cores = 0,16) stop: 2023-04-18 14:28:01+0000
  -m MODEL_VARIABLES, --model-variables MODEL_VARIABLES
                        Comma-separated list of variables to use in the regression model.
  -a ACTUAL_TIMESTAMPS_LIST, --actual-timestamps-list ACTUAL_TIMESTAMPS_LIST
                        Comma-separated list of files storing time series timestamps from actual values of load and energy to test
                        the model (in same format as train timestamps). If any file is specified train data will be split into train and test data.
  -o OUTPUT, --output OUTPUT
                        Directory to save time series plots and results. By default is './out'.
  -n NAME, --name NAME  Name of the model. It is useful to generate models from different sets of experiments in an orderly manner. By default is 'General'
```

Timestamps files must be stored in the following format:
```shell
<EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-START>
<EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-STOP>
```
With the following meaning:
- `EXP-NAME`: User desired name.
- `TYPE-OF-EXPERIMENT`: The type of experiment run during that period. It can take 3 values: STRESS-TEST if it's a stress test, IDLE if it's a period in which the CPU is idle and REAL-VALUES if it's a period in which test data was obtained.
- `DATE-START` and `DATE-STOP`: Timestamp of the beginning or end of the experiment in UTC format `%Y-%m-%d %H:%M:%S%z`.

Example:
```shell
Group_P (cores = 0,1) start: 2023-04-21 09:33:53+0000
Group_P (cores = 0,1) stop: 2023-04-21 09:35:54+0000
Group_P (cores = 0,1,2,3) start: 2023-04-21 09:36:24+0000
Group_P (cores = 0,1,2,3) stop: 2023-04-21 09:38:24+0000
Group_P (cores = 0,1,2,3,4,5) start: 2023-04-21 09:38:54+0000
Group_P (cores = 0,1,2,3,4,5) stop: 2023-04-21 09:40:54+0000
Group_P (cores = 0,1,2,3,4,5,6,7) start: 2023-04-21 09:41:24+0000
Group_P (cores = 0,1,2,3,4,5,6,7) stop: 2023-04-21 09:43:25+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9) start: 2023-04-21 09:43:55+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9) stop: 2023-04-21 09:45:56+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9,10,11) start: 2023-04-21 09:46:26+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9,10,11) stop: 2023-04-21 09:48:26+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9,10,11,12,13) start: 2023-04-21 09:48:56+0000
Group_P (cores = 0,1,2,3,4,5,6,7,8,9,10,11,12,13) stop: 2023-04-21 09:50:57+0000
```