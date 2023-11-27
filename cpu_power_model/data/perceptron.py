from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np

from cpu_power_model.config import config
from cpu_power_model.logs.logger import log


class Model:

    def __set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler = StandardScaler()
        self.X_train = self.scaler.fit_transform(X_train)
        self.y_train = y_train
        self.X_test = self.scaler.fit_transform(X_test)
        self.y_test = y_test

    def __set_model(self):
        model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, alpha=1e-4, solver='adam',
                             verbose=True, random_state=1, learning_rate_init=0.001, n_iter_no_change=20, tol=1e-5)
        model.fit(self.X_train, self.y_train.ravel())
        self.regression = model

    def __init__(self, name, idle, X, y):
        self.name = name
        self.idle_consumption = idle
        self.y_pred = None
        self.X_actual = None
        self.y_actual = None
        self.y_pred_actual = None
        self.__set_train_and_test_data(X, y)
        self.__set_model()

    def predict_test_values(self):
        self.y_pred = self.regression.predict(self.X_test)

    def predict_actual_values(self):
        self.y_pred_actual = self.regression.predict(self.X_actual)

    def predict(self):
        self.predict_test_values()
        if self.X_actual is not None:
            self.predict_actual_values()

    def set_actual_values(self, X, y):
        if X is not None and y is not None:
            self.X_actual = self.scaler.fit_transform(X)
            self.y_actual = y

    def write_performance(self, expected, predicted):
        results_file = f'{config.test_results_dir}/{config.model_name}-results.out'
        norm_factor = np.max(expected) - np.min(expected)
        rmse = mean_squared_error(expected, predicted, squared=False)
        with open(results_file, 'w') as file:
            file.write(f"MODEL NAME: {self.name}\n")
            file.write(f"NRMSE: {rmse/norm_factor}\n")
            file.write(f"R2 SCORE: {r2_score(expected, predicted)}\n")
            file.write("\n")
        log(f'Performance report and plots stored at {config.output_dir}')
