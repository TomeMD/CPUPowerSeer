from utils import config
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np

equation_x_vars = ["U_cpu", "F_cpu", "U_cpu^2", "(U_cpu*F_cpu)", "F_cpu^2"]
#equation_x_vars = ["U_cpu", "U_cpu^2"]

class Model:

    def __set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.poly_features = PolynomialFeatures(degree=2)
        self.X_poly_train = self.poly_features.fit_transform(X_train)
        self.y_train = y_train
        self.X_poly_test = self.poly_features.transform(X_test)
        self.y_test = y_test

    def __set_model(self):
        model = LinearRegression()
        model.fit(self.X_poly_train, self.y_train)
        self.poly_reg = model

    def __set_model_equation(self):
        eq_lines = [
            f"IDLE CONSUMPTION: {self.idle_consumption:.0f} J\n",
            f"EQUATION: y = {self.poly_reg.intercept_[0]:.0f}",
            *(
                f" + {self.poly_reg.coef_[0][i+1]:.8f}*{name}"
                for i, name in enumerate(equation_x_vars)
            )
        ]
        self.equation = "".join(eq_lines)

    def __init__(self, name, idle, X, y):
        self.name = name
        self.idle_consumption = idle
        self.y_poly_pred = None
        self.__set_train_and_test_data(X, y)
        self.__set_model()
        self.__set_model_equation()

    def predict_values(self):
        self.y_poly_pred = self.poly_reg.predict(self.X_poly_test)

    def update_test_values(self, X, y):
        if (X is not None and y is not None):
            self.X_poly_test = self.poly_features.transform(X)
            self.y_test = y

    def write_model_performance(self):
        results_file = f'{config.output_dir}/{config.model_name}-results.out'
        norm_factor = np.max(self.y_test) - np.min(self.y_test)
        rmse = mean_squared_error(self.y_test, self.y_poly_pred, squared=False)
        with open(results_file, 'w') as file:
            file.write(f"MODEL NAME: {self.name}\n")
            file.write(f"NRMSE: {rmse/norm_factor}\n")
            file.write(f"R2 SCORE: {r2_score(self.y_test, self.y_poly_pred)}\n")
            file.write(f"{self.equation}")
            file.write("\n")
        print(f'Performance report and plots stored at {config.output_dir}')
