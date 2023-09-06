# CPU Power Consumption Modeling

This tool builds a model to predict CPU energy consumption from CPU utilization and frequency using InfluxDB time series.

## Requirements

You need to install the following libraries:

```python
pip install influxdb-client pandas numpy scikit-learn matplotlib seaborn
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

### Options

```shell
usage: main.py [-h] [-t TRAIN_TIMESTAMPS] [-a ACTUAL_TIMESTAMPS] [-tp TRAIN_DATA_PLOT] [-ap ACTUAL_DATA_PLOT] [-n NAME]

Modeling CPU power consumption from InfluxDB time series.

options:
  -h, --help            show this help message and exit
  -t TRAIN_TIMESTAMPS, --train-timestamps TRAIN_TIMESTAMPS
                        File storing time series timestamps from train data. By default is log/stress.timestamps. Timestamps must be stored in the following format:
                             <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-START>
                             <EXP-NAME> <TYPE-OF-EXPERIMENT> ... <DATE-STOP>
                         Example:
                             Spread_P&L STRESS-TEST (cores = 0,16) start: 2023-04-18 14:26:01+0000
                             Spread_P&L STRESS-TEST (cores = 0,16) stop: 2023-04-18 14:28:01+0000
  -a ACTUAL_TIMESTAMPS, --actual-timestamps ACTUAL_TIMESTAMPS
                        File storing time series timestamps from actual values of load and energy to test the model (in same format as train timestamps). If not 
                                 specified train data will be split into train and test data.
  -tp TRAIN_DATA_PLOT, --train-data-plot TRAIN_DATA_PLOT
                        Specifies the path to save the train data time series plot. By default is 'img/train-data.png'.
  -ap ACTUAL_DATA_PLOT, --actual-data-plot ACTUAL_DATA_PLOT
                        Specifies the path to save the actual data time series plot. By default is 'img/actual-data.png'.
  -n NAME, --name NAME  Name of the model. It is useful to generate models from different sets of experiments in an orderly manner. By default is 'EC-CPU-MODEL'
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