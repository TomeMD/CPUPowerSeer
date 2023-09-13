import os

f_train_timestamps = None
f_actual_timestamps = None
output_dir = None
img_dir = None
model_name = None
x_vars = ["load", "freq"]
train_range = 1.5
test_range = 1.5  # 0.001


def set_config(args):
    global f_train_timestamps, f_actual_timestamps, model_name, output_dir, img_dir
    f_train_timestamps = args.train_timestamps
    f_actual_timestamps = args.actual_timestamps
    model_name = args.name
    output_dir = args.output
    img_dir = f'{output_dir}/img'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
