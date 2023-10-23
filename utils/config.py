import os
from utils.logger import log

verbose = None
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


def check_x_vars():
    aux = set(x_vars) - set(supported_vars)
    if any(var not in supported_vars for var in x_vars):
        log(f"{aux} not supported. Supported vars: {supported_vars}", "ERR")
        exit(1)


def check_files():
    if not os.path.exists(f_train_timestamps):
        log(f"Specified non existent actual timestamps file: {f_train_timestamps}.", "ERR")
        exit(1)
    if actual and not os.path.exists(f_actual_timestamps):
        log(f"Specified non existent actual timestamps file: {f_actual_timestamps}.", "ERR")
        exit(1)


def check_args():
    check_x_vars()
    check_files()


def set_config(args):
    global verbose, f_train_timestamps, f_actual_timestamps, actual, model_name, x_vars, output_dir, img_dir, log_file
    verbose = args.verbose
    f_train_timestamps = args.train_timestamps
    f_actual_timestamps = args.actual_timestamps
    actual = (f_actual_timestamps is not None)
    model_name = args.name
    x_vars = args.model_variables.split(',')
    output_dir = args.output
    img_dir = f'{output_dir}/img'
    log_file = f'{output_dir}/{model_name}.log'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)


def print_config():
    log(f"Model name: {model_name}")
    log(f"Train data timestamps file: {f_train_timestamps}")
    log(f"Actual (test) data timestamps file: {f_actual_timestamps}")
    log(f"Model variables: {x_vars}")
    log(f"Output directory: {output_dir}")
