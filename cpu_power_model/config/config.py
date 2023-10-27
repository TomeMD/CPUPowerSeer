verbose = None
interactive = None
influxdb_bucket = None
f_train_timestamps = None
f_actual_timestamps = None
actual = None
output_dir = None
img_dir = None
log_file = None
model_name = None
x_vars = None
train_range = 1.5
test_range = 1.5

supported_vars = ["load", "user_load", "system_load", "wait_load", "freq", "temp"]

x_var_label = {
    "load": "Utilization (%)",
    "user_load": "User Utilization (%)",
    "system_load": "System Utilization (%)",
    "wait_load": "IO Wait Utilization (%)",
    "freq": "Frequency (MHz)",
    "temp": "Temperature Cº"
}

x_var_eq = {
    "load": "U_cpu",
    "user_load": "U_user",
    "system_load": "U_system",
    "wait_load": "U_wait",
    "freq": "F_cpu",
    "temp": "T_cpu"
}

x_var_color = {
    "load": "tab:blue",
    "user_load": "tab:blue",
    "system_load": "tab:purple",
    "wait_load": "tab:green",
    "freq": "tab:red",
    "temp": "tab:pink"
}