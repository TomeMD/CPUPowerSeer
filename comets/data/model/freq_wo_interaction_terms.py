from sklearn.model_selection import train_test_split
import numpy as np

from comets.data.model.polynomial import PolynomialModel, generate_monomials
from comets.config import config


class FreqWoInteractionTerms(PolynomialModel):
    def __init__(self, name):
        super().__init__(name)
        if "freq" in config.x_vars:
            self.freq_var = "custom_freq"
        elif "sumfreq" in config.x_vars:
            self.freq_var = "sumfreq"

    def get_custom_freq(self, frequency, user, system):
        if self.freq_var == "custom_freq":
            return frequency * (user + system)
        elif self.freq_var == "sumfreq":
            return frequency

    def set_train_and_test_data(self, X, y):
            user = X[:, 0]
            system = X[:, 1]
            frequency = X[:, 2]
            user_system = user * system
            user_squared = user ** 2
            system_squared = system ** 2
            custom_freq = self.get_custom_freq(frequency, user, system)
            X_custom = np.column_stack([user, system, user_system,
                                        user_squared, system_squared, custom_freq])
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
            custom_freq = self.get_custom_freq(frequency, user, system)
            self.X_actual = np.column_stack([user, system, user_system,
                                             user_squared, system_squared, custom_freq])
            self.y_actual = y

    def set_equation(self, idle_consumption):
        names_list = [config.x_var_eq[var] for var in config.x_vars if var != 'freq' and var != 'sumfreq']
        eq_lines = [
            f"IDLE CONSUMPTION: {idle_consumption:.0f} J\n",
            f"EQUATION: y = {self.model.intercept_[0]:.0f}",
            *(
                f" + {self.model.coef_[0][i]:.8f}*{name}"
                for i, name in enumerate(generate_monomials(names_list))
            ),
            f" + {self.model.coef_[0][5]:.16f}*{config.x_var_eq[self.freq_var]}"
        ]
        self.equation = "".join(eq_lines)
