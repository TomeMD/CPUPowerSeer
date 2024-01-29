from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import pandas as pd

from cpu_power_seer.data.model.model import Model
from cpu_power_seer.logs.logger import log


param_grid = {
    'hidden_layer_sizes': [(2, 2), (3, 3), (10, 10), (50, ), (50, 50), (100, ), (100, 100)],
    'alpha': [1.e-01, 1.e-02, 1.e-03, 1.e-04, 1.e-05, 1.e-06],
    'learning_rate_init': [1.e-01, 1.e-02, 1.e-03, 1.e-04],
    'solver': ['sgd', 'adam', 'lbfgs'],
    'momentum': [0, 0.9],
    'nesterovs_momentum': [True, False],
    'max_iter': [500, 1000, 1500]
}


class PerceptronModel(Model):

    def __init__(self, name):
        super().__init__(name)
        self.scaler = None
        self.grid_search = None

    def set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler = StandardScaler()
        self.scaler.fit(X_train)
        self.X_train = self.scaler.transform(X_train)
        self.y_train = y_train
        self.X_test = self.scaler.transform(X_test)
        self.y_test = y_test

    def set_actual_values(self, X, y):
        if X is not None and y is not None:
            self.X_actual = self.scaler.transform(X)
            self.y_actual = y

    def set_model(self):
        mlp = MLPRegressor(verbose=True, random_state=1, n_iter_no_change=20, tol=1e-5)
        self.grid_search = GridSearchCV(mlp, param_grid,
                                        scoring='neg_mean_absolute_percentage_error', cv=5, n_jobs=-1, verbose=2)

    def train(self):
        log("Searching for the best configuration by cross-validation")
        self.grid_search.fit(self.X_train, self.y_train.ravel())
        log(f"Found best model parameters {self.grid_search.best_params_} (Mean score: {-self.grid_search.best_score_})")
        self.model = self.grid_search.best_estimator_
        cv_results = pd.DataFrame(self.grid_search.cv_results_)
        log(cv_results)
