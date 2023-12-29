from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from comets.config import config
from comets.data.model.utils import generate_monomials
from comets.data.model.model import Model


class PolynomialModel(Model):
    def set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.poly_features = PolynomialFeatures(degree=2)
        self.X_train = self.poly_features.fit_transform(X_train)
        self.y_train = y_train
        self.X_test = self.poly_features.transform(X_test)
        self.y_test = y_test

    def set_actual_values(self, X, y):
        if X is not None and y is not None:
            self.X_actual = self.poly_features.transform(X)
            self.y_actual = y

    def set_equation(self, idle_consumption):
        names_list = [config.x_var_eq[var] for var in config.x_vars]
        eq_lines = [
            f"IDLE CONSUMPTION: {idle_consumption:.0f} J\n",
            f"EQUATION: y = {self.model.intercept_[0]:.0f}",
            *(
                f" + {self.model.coef_[0][i+1]:.8f}*{name}"
                for i, name in enumerate(generate_monomials(names_list))
            )
        ]
        self.equation = "".join(eq_lines)

    def set_model(self):
        self.model = LinearRegression()
