from cpu_power_seer.data.plot.utils import *


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
    set_legend_with_markers(ax1, ax2)
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
    X_not_squared_position = 0
    if hasattr(model, 'poly_features') and model.poly_features is not None:
        X_not_squared_position = 1

    X_idx = model.X_test[:, X_not_squared_position].argsort()
    X_test = model.X_test
    if hasattr(model, 'scaler') and model.scaler is not None:
        X_test = model.scaler.inverse_transform(X_test)
    X_sorted = X_test[X_idx]
    y_sorted = model.y_pred[X_idx].ravel()

    fig = plt.figure()
    sns.lineplot(x=X_sorted[:, X_not_squared_position], y=y_sorted, ax=plt.gca(), color=config.x_var_color[var], label="Polynomial regression")
    set_basic_labels("Model Function", config.x_var_label[var], "Power Consumption (W)", plt.gca())
    plt.legend()
    save_plot(filename)
    plt.close(fig)
