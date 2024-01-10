from sklearn.metrics import mean_squared_error, r2_score, max_error, mean_absolute_error, mean_absolute_percentage_error
import numpy as np

from cpu_power_seer.config import config
from cpu_power_seer.logs.logger import log


def r2_adj_score(expected, predicted, r2=None):
    n = len(expected)
    k = len(config.x_vars)
    if n != len(predicted):
        log(f"Number of real samples ({n}) doesn't match number of predicted values ({len(predicted)})", "ERR")
        exit(1)
    if r2 is None:
        r2 = r2_score(expected, predicted)
    if (n - 1 - k) <= 0:  # Avoid division by zero or R2adj > 1 [Extreme case k >= n-1]
        return 0
    return 1 - ((n - 1)/(n - 1 - k)) * (1 - r2)


def generate_monomials(X):
    monomials = X.copy()
    for i in range(len(X)):
        monomials.append(f"{X[i]}²")
        for j in range(i + 1, len(X)):
            monomials.append(f"{X[i]}×{X[j]}")
    return monomials


def write_value(value_name, value, test_name):
    results_file = f'{config.test_dir}/{value_name}-summary.out'
    with open(results_file, 'a') as file:
        file.write(f"{test_name} {value_name}: {value}\n")


def write_performance(model_name, expected, predicted, write_summary=False, test_name=None, equation=None):
    results_file = f'{config.test_results_dir}/{config.model_name}-results.out'
    max_err = max_error(expected, predicted)
    mae = mean_absolute_error(expected, predicted)
    mape = mean_absolute_percentage_error(expected, predicted)
    norm_factor = np.max(expected) - np.min(expected)
    rmse = mean_squared_error(expected, predicted, squared=False)
    r2 = r2_score(expected, predicted)
    r2_adj = r2_adj_score(expected, predicted, r2)
    with open(results_file, 'w') as file:
        file.write(f"MODEL NAME: {model_name}\n")
        file.write(f"MAX ERROR: {max_err}\n")
        file.write(f"MAE: {mae}\n")
        file.write(f"MAPE: {mape}\n")
        file.write(f"RMSE: {rmse}\n")
        file.write(f"NRMSE: {rmse/norm_factor}\n")
        file.write(f"R2 SCORE: {r2}\n")
        file.write(f"R2 ADJUSTED: {r2_adj}\n")
        if equation is not None:
            file.write(f"{equation}")
        file.write("\n")
    if write_summary:
        write_value("R2", r2, test_name)
        write_value("MAPE", mape, test_name)
