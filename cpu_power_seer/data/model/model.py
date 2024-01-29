from joblib import dump


class Model:

    def __init__(self, name):
        self.name = name
        self.poly_features = None
        self.X_train = None
        self.y_train = None
        self.X_test = None
        self.y_test = None
        self.X_actual = None
        self.y_actual = None
        self.y_pred = None
        self.y_pred_actual = None
        self.model = None
        self.equation = None

    def set_equation(self, idle_consumption):
        self.equation = None

    def predict_test_values(self):
        self.y_pred = self.model.predict(self.X_test)

    def predict_actual_values(self):
        self.y_pred_actual = self.model.predict(self.X_actual)

    def train(self):
        self.model.fit(self.X_train, self.y_train)

    def test(self):
        self.predict_test_values()
        if self.X_actual is not None:
            self.predict_actual_values()

    def save_model(self, path):
        dump(self.model, path)
