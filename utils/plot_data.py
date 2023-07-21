import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator

def plot_time_series(df, title, xlabel, ylabels, path):
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

def plot_model(model, actual_values, X_poly_test, y_poly_pred, idle_consumption, path):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(X_poly_test[:, 0], X_poly_test[:, 1], y_poly_pred, color='red', label='Valores predichos')
    if (actual_values[0] is not None and actual_values[1] is not None):
        ax.scatter(actual_values[0], actual_values[1], color="green", label="Datos de test (custom)")

    ax.set_xlabel('Utilización de CPU')
    ax.set_ylabel('Frecuencia de CPU')
    ax.set_zlabel('Consumo energético')
    ax.legend()

    title_lines = [
        f"Polinómica: y = {model.intercept_[0]:.0f}",
        *(
            f" + {model.coef_[0][i+1]:.8f}*{name}"
            for i, name in enumerate(["U_cpu", "F_cpu", "(U_cpu*F_cpu)", "U_cpu^2", "F_cpu^2"])
        ),
        f"\nConsumo en reposo: {idle_consumption:.0f} J"
    ]
    title = "\n".join(title_lines)

    plt.title(title)
    plt.tight_layout()
    plt.savefig(path)
