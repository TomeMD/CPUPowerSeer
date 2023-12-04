from sklearn.metrics import mean_squared_error, r2_score, max_error, mean_absolute_error, mean_absolute_percentage_error
import numpy as np

from cpu_power_model.config import config
from cpu_power_model.logs.logger import log


def generate_monomials(X):
    monomials = X.copy()
    for i in range(len(X)):
        monomials.append(f"{X[i]}²")
        for j in range(i + 1, len(X)):
            monomials.append(f"{X[i]}×{X[j]}")
    return monomials


def write_r2(r2, test_name):
    results_file = f'{config.test_dir}/{config.model_name}-results.out'
    with open(results_file, 'a') as file:
        file.write(f"{test_name} R2: {r2}\n")


def write_performance(model_name, expected, predicted, write_common_file=False, test_name=None, equation=None):
    results_file = f'{config.test_results_dir}/{config.model_name}-results.out'
    max_err = max_error(expected, predicted)
    mae = mean_absolute_error(expected, predicted)
    mape = mean_absolute_percentage_error(expected, predicted)
    norm_factor = np.max(expected) - np.min(expected)
    rmse = mean_squared_error(expected, predicted, squared=False)
    r2 = r2_score(expected, predicted)
    with open(results_file, 'w') as file:
        file.write(f"MODEL NAME: {model_name}\n")
        file.write(f"MAX ERROR: {max_err}\n")
        file.write(f"MAE: {mae}\n")
        file.write(f"MAPE: {mape}\n")
        file.write(f"RMSE: {rmse}\n")
        file.write(f"NRMSE: {rmse/norm_factor}\n")
        file.write(f"R2 SCORE: {r2}\n")
        if equation is not None:
            file.write(f"{equation}")
        file.write("\n")
    if write_common_file:
        write_r2(r2, test_name)
    log(f'Performance report and plots stored at {config.output_dir}')
