# COMETS: CPU Power Modeling from Time Series

This tool builds a model to predict CPU power consumption from different CPU variables (Utilization, Frequency,...) using InfluxDB time series.

- [Configuration](#configuration)
- [Installation](#installation)
- [Execution and options](#execution)
- [Output](#output)

<a name="configuration"></a>
## Configuration

Before using this tool you must configure the InfluxDB server from which the metrics will be exported, as well as the timestamps of the time series you want to obtain from that server.

### InfluxDB server

To modify your InfluxDB server simply modify the following code variables from `comets.influxdb.influxdb_env.py`:

```python
INFLUXDB_URL = "influxdb-server:port"
INFLUXDB_TOKEN = "your-token"
INFLUXDB_ORG = "your-org"
```

It is assumed that this server stores Glances and RAPL metrics in a proper format. 

*Note: To store this metrics properly see [**CROWDS**](https://github.com/TomeMD/crowds.git).*

<a name="installation"></a>
## Installation

First of all, you can (and should) create a virtual environment by running:

```
python -m venv my_venv
source my_venv/bin/activate
```

To install and use this tool run:

```
pip install .
```

If you only want to install the project dependencies, run:

```
pip install -r requirements.txt
```

Finally, when you no longer want to use COMETS, you can deactivate your virtual environment by running:

``` 
deactivate
```
<a name="execution"></a>
## Execution and options

```shell
usage: comets [-h] [-v] --vars VARS -t TRAIN_TIMESTAMPS [-a ACTUAL_TIMESTAMPS_LIST] [-p PREDICTION_METHOD] [-b BUCKET] [-o OUTPUT] [-n NAME]

CPU Power Modeling from Time Series.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  --vars VARS           Comma-separated list of variables to use in the regression model. Commonly known as predictor variables.
                        Supported values: user_load, system_load, wait_load, freq, sumfreq.
  -t TRAIN_TIMESTAMPS, --train-timestamps TRAIN_TIMESTAMPS
                        File storing time series timestamps from train data in proper format. Check README.md to see timestamps proper format.
  -a ACTUAL_TIMESTAMPS_LIST, --actual-timestamps-list ACTUAL_TIMESTAMPS_LIST
                        Comma-separated list of files storing time series timestamps from actual values of predictor variables and power to test
                        the model (in same format as train timestamps). If any file is specified train data will be split into train and test data.
  -p PREDICTION_METHOD, --prediction-method PREDICTION_METHOD
                        Method used to predict CPU power consumption. By default is a polynomial regression. Supported methods:
                                polynomial                      Polynomial Regression with specified variables
                                freqwointeractionterms          Custom Regression using user_load, system_load and freq or sumfreq
                                perceptron                      Multilayer Perceptron
  -b BUCKET, --bucket BUCKET
                        InfluxDB Bucket to retrieve data from. By default is 'mybucket'.
  -o OUTPUT, --output OUTPUT
                        Directory to save time series plots and results. By default is './out'.
  -n NAME, --name NAME  Name of the model. It is useful to generate models from different sets of experiments in an orderly manner. By default is 'General'
```

Timestamps files must be stored in the following format:
```shell
<EXP-NAME> <TYPE-OF-EXPERIMENT> (CORES = <CORES>) START: <START-DATE>
<EXP-NAME> <TYPE-OF-EXPERIMENT> (CORES = <CORES>) STOP: <STOP-DATE>
```
With the following meaning:
- `EXP-NAME`: User desired name.
- `TYPE-OF-EXPERIMENT`: The type of experiment run during that period. It can take 3 values: STRESS-TEST if it's a stress test, IDLE if it's a period in which the CPU is idle and other if it's a period in which test data was obtained.
- `CORES`: Comma-separated list of cores used in the experiment.
- `START-DATE` and `STOP-DATE`: Timestamp of the beginning or end of the experiment in UTC format `%Y-%m-%d %H:%M:%S%z`.

Example:
```shell
Group_P STRESS-TEST (CORES = 0,1) START: 2023-04-21 09:33:53+0000
Group_P STRESS-TEST (CORES = 0,1) STOP: 2023-04-21 09:35:54+0000
Group_P STRESS-TEST (CORES = 0,1,2,3) START: 2023-04-21 09:36:24+0000
Group_P STRESS-TEST (CORES = 0,1,2,3) STOP: 2023-04-21 09:38:24+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5) START: 2023-04-21 09:38:54+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5) STOP: 2023-04-21 09:40:54+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7) START: 2023-04-21 09:41:24+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7) STOP: 2023-04-21 09:43:25+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9) START: 2023-04-21 09:43:55+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9) STOP: 2023-04-21 09:45:56+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9,10,11) START: 2023-04-21 09:46:26+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9,10,11) STOP: 2023-04-21 09:48:26+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9,10,11,12,13) START: 2023-04-21 09:48:56+0000
Group_P STRESS-TEST (CORES = 0,1,2,3,4,5,6,7,8,9,10,11,12,13) STOP: 2023-04-21 09:50:57+0000
```

*Note: To obtain timestamps files in proper format see [**CROWDS**](https://github.com/TomeMD/crowds.git).*
<a name="output"></a>
## Output

Output will be stored in the specified directory (-o option) or './out' by default. In the output directory you will find 2 subdirectories, train and test, which contains train time series and test/predictions time series along with their results, respectively. The directory tree will have the following appearance:

```shell
out
|
├─── train
|	├─── <MODEL-NAME>-temperature-data.png				Temperature train time series
|	└─── <MODEL-NAME>-train-data.png				Model variables train time series
|
|
└─── test
	├─── <MODEL-NAME>-summary.out					Summary of the results obtained with all benchmarks.
	└─── <BENCHMARK>
		├─── <MODEL-NAME>-results.out				Benchmark results
		├─── img
		|	├─── <MODEL-NAME>-results.png			Expected VS Predicted Points plot
		|	└─── <MODEL-NAME>-predictions.png		Predicted time series
		|
		├─── <THREADS[0]>
		|	├─── <MODEL-NAME>-results.png			Benchmark results with <THREADS[0]> threads
		|	└─── img
		|		├─── <MODEL-NAME>-results.png		Expected VS Predicted Points plot with <THREADS[0]> threads
		|		└─── <MODEL-NAME>-predictions.png	Predicted time series with <THREADS[0]> threads
		├─── ...
		|
		└─── <THREADS[n]>
```

There will be one subdirectory in benchmark directory for each number of threads used with this benchmark. 

***Note: Don't forget to specify the cores in the timestamps file because COMETS will infer the number of threads/cores used from these files.***