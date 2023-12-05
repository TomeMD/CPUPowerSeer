from sklearn.model_selection import train_test_split
import numpy as np

from cpu_power_model.data.model.polynomial import PolynomialModel, generate_monomials
from cpu_power_model.config import config


class FreqByLoadModel(PolynomialModel):

    def set_train_and_test_data(self, X, y):
        user = X[:, 0]
        system = X[:, 1]
        frequency = X[:, 2]
        user_system = user * system
        user_squared = user ** 2
        system_squared = system ** 2
        user_system_squared = user_squared * system_squared
        freq_user_system = frequency * (user + system)
        X_custom = np.column_stack([user, system, user_system,
                                    user_squared, system_squared, user_system_squared, freq_user_system])
        X_train, X_test, y_train, y_test = train_test_split(X_custom, y, test_size=0.2, random_state=42)
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def set_actual_values(self, X, y):
        if X is not None and y is not None:
            user = X[:, 0]
            system = X[:, 1]
            frequency = X[:, 2]
            user_system = user * system
            user_squared = user ** 2
            system_squared = system ** 2
            user_system_squared = user_squared * system_squared
            freq_user_system = frequency * (user + system)

            self.X_actual = np.column_stack([user, system, user_system,
                                             user_squared, system_squared, user_system_squared, freq_user_system])
            self.y_actual = y

    def set_equation(self, idle_consumption):
        names_list = [config.x_var_eq[var] for var in config.x_vars if var != 'freq']
        eq_lines = [
            f"IDLE CONSUMPTION: {idle_consumption:.0f} J\n",
            f"EQUATION: y = {self.model.intercept_[0]:.0f}",
            *(
                f" + {self.model.coef_[0][i+1]:.8f}*{name}"
                for i, name in enumerate(generate_monomials(names_list))
            ),
            f" + {self.model.coef_[0][6]:.16f}*F_cpu*(U_user+U_system)"
        ]
        self.equation = "".join(eq_lines)
