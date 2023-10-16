import os

f_train_timestamps = None
f_actual_timestamps = None
actual = None
output_dir = None
img_dir = None
model_name = None
x_vars = None
train_range = 1.5
test_range = 1.5  # 0.001

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


def set_config(args):
    global f_train_timestamps, f_actual_timestamps, actual, model_name, x_vars, output_dir, img_dir
    f_train_timestamps = args.train_timestamps
    f_actual_timestamps = args.actual_timestamps
    actual = (f_actual_timestamps is not None)
    model_name = args.name
    x_vars = args.model_variables.split(',')
    output_dir = args.output
    img_dir = f'{output_dir}/img'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
