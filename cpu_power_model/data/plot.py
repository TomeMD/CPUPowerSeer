import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator

from cpu_power_model.config import config


def set_basic_labels(title, xlabel, ylabel, ax):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def save_plot(filename, tight_layout=True):
    path = f'{config.img_dir}/{filename}'
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')


def set_line_plot(x, y, ax, color=None, label=None, linestyle="solid"):
    sns.lineplot(x=x, y=y, ax=ax, color=color, label=label, linestyle=linestyle)


def set_time_axis(ax):
    for label in ax.get_xticklabels():
        label.set_rotation(45)
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


def set_legend(ax1, ax2):
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='center left', bbox_to_anchor=(0, 1.5))
    ax2.get_legend().remove()


def plot_time_series(title, df, x_vars, filename, show_predictions=False):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    # Plot 1 line for each predictor variable (Left Axis: ax1)
    for var in x_vars:
        set_line_plot(df["time"], df[var], ax1, config.x_var_color[var], config.x_var_label[var])
    # Plot dependent variable "power" (Right Axis: ax2)
    set_line_plot(df["time"], df["energy"], ax2, 'tab:orange', "Power Consumption (W)")
    # Plot predicted power if provided (Right Axis: ax2)
    if show_predictions:
        set_line_plot(df["time"], df["energy_predicted"], ax2, 'tab:green', "Predicted Power Consumption (W)", "dashed")
    set_time_axis(ax1)
    set_basic_labels(title, "Time HH:MM", "CPU Model Variables", ax1)
    set_basic_labels(None, None, "Power Consumption (W)", ax2)
    set_legend(ax1, ax2)
    save_plot(filename)
    plt.close(fig)


def plot_var(title, df, var, filename):
    fig = plt.figure()
    set_line_plot(df["time"], df[var], plt.gca(), config.x_var_color[var])
    set_time_axis(plt.gca())
    set_basic_labels(title, "Time (HH:MM)", config.x_var_label[var], plt.gca())
    save_plot(filename)
    plt.close(fig)


def plot_results(expected, predicted, filename):
    fig = plt.figure()
    expected.shape = (-1)
    predicted.shape = (-1)
    sns.scatterplot(x=expected, y=predicted, label='Forecasts', color='tab:orange')
    max_val = max(max(expected), max(predicted))
    set_line_plot([0, max_val], [0, max_val], plt.gca(), 'black', 'Ideal Scenario')
    set_basic_labels('Expected VS Predicted', 'Expected values', 'Predicted values', plt.gca())
    plt.legend()
    save_plot(filename)
    plt.close(fig)


def plot_model(model, var, filename):
    X_idx = model.X_test[:, 1].argsort()
    X_sorted = model.X_test[X_idx]
    y_sorted = model.y_pred[X_idx].ravel()
    fig = plt.figure()
    set_line_plot(X_sorted[:, 1], y_sorted, plt.gca(), config.x_var_color[var], "Polynomial regression")
    set_basic_labels("Model Function", config.x_var_label[var], "Power Consumption (W)", plt.gca())
    plt.legend()
    save_plot(filename)
    plt.close(fig)
