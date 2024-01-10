import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
from matplotlib.lines import Line2D

from cpu_power_seer.config import config

# Use a non-interactive backend to avoid the requirement of being run from the main thread
# Exception: main thread is not in main loop
plt.switch_backend('agg')


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


def set_basic_legend(ax1, ax2):
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="center left", bbox_to_anchor=(0, 1.5))
    ax2.get_legend().remove()


def set_legend_with_markers(ax1, ax2):
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
