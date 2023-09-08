from utils import config
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator


def plot_time_series(df, title, xlabel, ylabels, filename):
    path = f'{config.img_dir}/{filename}'
    print(f'Saving plot in {path}')
    plt.figure()
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    # Set CPU Utilization axis
    sns.lineplot(x=df["_time"], y=df["_value_load"], label="Utilización de CPU", ax=ax1)
    sns.lineplot(x=df["_time"], y=df["_value_freq"], label="Frecuencia de CPU", ax=ax1,color='tab:green')
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabels[0] + " / " + ylabels[1])
    ax1.tick_params(axis='y')
    for label in ax1.get_xticklabels():
        label.set_rotation(45)

    # Set Energy Consumption axis
    sns.lineplot(x=df["_time"], y=df["_value_energy"], label="Consumo energético", ax=ax2, color='tab:orange')
    ax2.set_ylabel(ylabels[2])
    ax2.tick_params(axis='y')
    ax2.set_ylim(0, 1000)

    # Set time axis
    plt.title(title)
    ax1.xaxis.set_major_locator(MinuteLocator(interval=10))
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))

    # Set legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    ax1.legend(lines, labels, loc='upper left')
    ax2.get_legend().remove()

    plt.tight_layout()
    plt.savefig(path)

def plot_3d_graph(ax, X_poly_test, y_poly_pred):
    ax.scatter(X_poly_test[:, 1], X_poly_test[:, 2], y_poly_pred, color='red', label='Valores predichos')
    ax.set_xlabel('Utilización de CPU')
    ax.set_ylabel('Frecuencia de CPU')
    ax.set_zlabel('Consumo energético')
    ax.legend()

def plot_2d_graph(ax, X, y, xlabel, ylabel):
    ax.scatter(X, y, color='red', label='Valores predichos')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()

def plot_model(model, actual_values, X_poly_test, y_poly_pred, filename):
    path = f'{config.img_dir}/{filename}'
    fig = plt.figure(figsize=(18, 6))

    # 3D plot
    ax1 = fig.add_subplot(131, projection='3d')
    plot_3d_graph(ax1, X_poly_test, y_poly_pred)

    # 2D plot for CPU utilization
    ax2 = fig.add_subplot(132)
    plot_2d_graph(ax2, X_poly_test[:, 1], y_poly_pred, 'Utilización de CPU', 'Consumo energético')

    # 2D plot for CPU frequency
    ax3 = fig.add_subplot(133)
    plot_2d_graph(ax3, X_poly_test[:, 2], y_poly_pred, 'Frecuencia de CPU', 'Consumo energético')

    plt.tight_layout()
    plt.savefig(path)
