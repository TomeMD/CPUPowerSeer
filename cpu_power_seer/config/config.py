verbose = None
influxdb_bucket = None
train_ts_file = None
test_ts_files_list = []
test_results_dir = None
train_dir = None
test_dir = None
output_dir = None
img_dir = None
log_file = None
model_name = None
x_vars = None
prediction_method = None

supported_vars = ["load", "user_load", "system_load", "wait_load", "freq", "sumfreq", "temp"]
supported_pred_methods = ["polynomial", "freqwointeractionterms", "perceptron", "custom"]

x_var_label = {
    "load": "Utilization (%)",
    "user_load": "User Utilization (%)",
    "system_load": "System Utilization (%)",
    "wait_load": "IO Wait Utilization (%)",
    "freq": "Avg Frequency (MHz)",
    "sumfreq": "Sum Frequency (MHz)",
    "temp": "Temperature Cº",
    "power": "Power Consumption (W)",
    "power_predicted": "Predicted Power Consumption (W)"
}

x_var_color = {
    "load": "#2b83ba",
    "user_load": "#2b83ba",
    "system_load": "#5e3c99",
    "wait_load": "#ffffbf",
    "freq": "#d7191c",
    "sumfreq": "#d7191c",
    "temp": "#f781bf",
    "power": "#fdae61",
    "power_predicted": "#008837"
}

x_var_marker = {
    "load": "o",
    "user_load": "o",
    "system_load": "s",
    "wait_load": "d",
    "freq": "X",
    "sumfreq": "X",
    "temp": None,
    "power": None,
    "power_predicted": None
}

x_var_eq = {
    "load": "U_cpu",
    "user_load": "U_user",
    "system_load": "U_system",
    "wait_load": "U_wait",
    "freq": "F_avg",
    "sumfreq": "F_sum",
    "custom_freq": "F_cpu*(U_user+U_system)",
    "temp": "T_cpu"
}