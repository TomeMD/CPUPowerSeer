import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
from matplotlib.lines import Line2D

from cpu_power_model.config import config


# It is assumed there's one key per value (config.py dicts)
def get_key_from_value(dict, value):
    for k, v in dict.items():
        if v == value:
            return k


def set_basic_labels(title, xlabel, ylabel, ax):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def save_plot(filename, tight_layout=True):
    path = f'{config.img_dir}/{filename}'
    if tight_layout:
        plt.tight_layout()
    plt.savefig(path, bbox_inches='tight')


def set_line_plot(var, df, ax):
    x = df["time_diff"]
    y = df[var]
    linestyle = "dashed" if var == "power_predicted" else "solid"
    color = config.x_var_color[var]
    label = config.x_var_label[var]
    marker = config.x_var_marker[var]
    sns.lineplot(x=x, y=y, ax=ax, color=color, label=label, linestyle=linestyle)
    if marker is not None:
        ax.scatter(x[::50], y[::50], s=20, color="black", marker=marker, zorder=3, edgecolors=color, linewidths=0.2)


def set_time_axis(ax):
    for label in ax.get_xticklabels():
        label.set_rotation(45)
    ax.xaxis.set_major_locator(AutoDateLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


# def set_legend(ax1, ax2):
#     lines1, labels1 = ax1.get_legend_handles_labels()
#     lines2, labels2 = ax2.get_legend_handles_labels()
#     ax1.legend(lines1 + lines2, labels1 + labels2, loc="center left", bbox_to_anchor=(0, 1.5))
#     ax2.get_legend().remove()


def set_legend(ax1, ax2):
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    custom_lines = []
    for line, label in zip(lines1 + lines2, labels1 + labels2):
        if isinstance(line, Line2D):
            var = get_key_from_value(config.x_var_label, label)
            custom_line = Line2D([0], [0], color=line.get_color(), markerfacecolor="black",
                                 marker=config.x_var_marker[var], markersize=10, label=label,
                                 linestyle=line.get_linestyle())
            custom_lines.append(custom_line)
    ax1.legend(handles=custom_lines, loc="center left", bbox_to_anchor=(0, 1.5))
    ax2.get_legend().remove()


def plot_time_series(title, df, x_vars, filename, show_predictions=False):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    # Plot 1 line for each predictor variable (Left Axis: ax1)
    for var in x_vars:
        set_line_plot(var, df, ax1)
    # Plot dependent variable "power" (Right Axis: ax2)
    set_line_plot("power", df, ax2)
    # Plot predicted power if provided (Right Axis: ax2)
    if show_predictions:
        set_line_plot("power_predicted", df, ax2)
    set_basic_labels(title, f"Time ({df['time_unit'].iloc[0]})", "CPU Model Variables", ax1)
    set_basic_labels(None, None, "Power Consumption (W)", ax2)
    set_legend(ax1, ax2)
    save_plot(filename)
    plt.close(fig)


def plot_var(title, df, var, filename):
    fig = plt.figure()
    set_line_plot(var, df, plt.gca())
    set_basic_labels(title, f"Time ({df['time_unit'].iloc[0]})", config.x_var_label[var], plt.gca())
    save_plot(filename)
    plt.close(fig)


def plot_results(expected, predicted, filename):
    fig = plt.figure()
    expected.shape = (-1)
    predicted.shape = (-1)
    sns.scatterplot(x=expected, y=predicted, label="Values", color='tab:orange')
    max_val = max(max(expected), max(predicted))
    sns.lineplot(x=[0, max_val], y=[0, max_val], ax=plt.gca(), color='black', label="Ideal Scenario")
    set_basic_labels("Expected VS Predicted", "Expected", "Predicted", plt.gca())
    plt.legend()
    save_plot(filename)
    plt.close(fig)


def plot_model(model, var, filename):
    X_idx = model.X_test[:, 1].argsort()
    X_sorted = model.X_test[X_idx]
    y_sorted = model.y_pred[X_idx].ravel()
    fig = plt.figure()
    sns.lineplot(x=X_sorted[:, 1], y=y_sorted, ax=plt.gca(), color=config.x_var_color[var], label="Polynomial regression")
    set_basic_labels("Model Function", config.x_var_label[var], "Power Consumption (W)", plt.gca())
    plt.legend()
    save_plot(filename)
    plt.close(fig)
