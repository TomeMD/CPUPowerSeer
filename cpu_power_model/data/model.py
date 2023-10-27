from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
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


class Model:

    def __set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.poly_features = PolynomialFeatures(degree=2)
        self.X_train = self.poly_features.fit_transform(X_train)
        self.y_train = y_train
        self.X_test = self.poly_features.transform(X_test)
        self.y_test = y_test

    def __set_model(self):
        model = LinearRegression()
        model.fit(self.X_train, self.y_train)
        self.regression = model

    def __set_model_equation(self):
        names_list = [config.x_var_eq[var] for var in config.x_vars]
        eq_lines = [
            f"IDLE CONSUMPTION: {self.idle_consumption:.0f} J\n",
            f"EQUATION: y = {self.regression.intercept_[0]:.0f}",
            *(
                f" + {self.regression.coef_[0][i+1]:.8f}*{name}"
                for i, name in enumerate(generate_monomials(names_list))
            )
        ]
        self.equation = "".join(eq_lines)

    def __init__(self, name, idle, X, y):
        self.name = name
        self.idle_consumption = idle
        self.y_pred = None
        self.X_actual = None
        self.y_actual = None
        self.y_pred_actual = None
        self.__set_train_and_test_data(X, y)
        self.__set_model()
        self.__set_model_equation()

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
            self.X_actual = self.poly_features.transform(X)
            self.y_actual = y

    def write_performance(self, expected, predicted):
        results_file = f'{config.output_dir}/{config.model_name}-results.out'
        norm_factor = np.max(expected) - np.min(expected)
        rmse = mean_squared_error(expected, predicted, squared=False)
        with open(results_file, 'w') as file:
            file.write(f"MODEL NAME: {self.name}\n")
            file.write(f"NRMSE: {rmse/norm_factor}\n")
            file.write(f"R2 SCORE: {r2_score(expected, predicted)}\n")
            file.write(f"{self.equation}")
            file.write("\n")
        log(f'Performance report and plots stored at {config.output_dir}')

    def write_model_performance(self, actual=False):
        if actual:
            self.write_performance(self.y_actual, self.y_pred_actual)
        else:
            self.write_performance(self.y_test, self.y_pred)
