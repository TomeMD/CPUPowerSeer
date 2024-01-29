from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler

from cpu_power_seer.data.model.model import Model


class SVRModel(Model):

    def __init__(self, name):
        super().__init__(name)
        self.scaler = None

    def set_train_and_test_data(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler = StandardScaler()
        self.X_train = self.scaler.fit_transform(X_train)
        self.y_train = y_train
        self.X_test = self.scaler.transform(X_test)
        self.y_test = y_test

    def set_actual_values(self, X, y):
        if X is not None and y is not None:
            self.X_actual = self.scaler.transform(X)
            self.y_actual = y

    def set_model(self):
        self.model = SVR(kernel="poly", degree=2)
