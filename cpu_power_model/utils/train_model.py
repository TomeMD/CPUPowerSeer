from cpu_power_model.config import config
from cpu_power_model.data.process import get_idle_consumption, get_formatted_vars
from cpu_power_model.data.model import PolynomialModel, FreqByLoadModel, PerceptronModel


def run(train_timestamps, time_series):

    idle_consumption = get_idle_consumption(train_timestamps, config.train_range)
    X, y = get_formatted_vars(config.x_vars, time_series)
    if config.prediction_method == "polynomial":
        model = PolynomialModel(config.model_name)
    elif config.prediction_method == "freqbyload":
        model = FreqByLoadModel(config.model_name)
    elif config.prediction_method == "perceptron":
        model = PerceptronModel(config.model_name)

    model.set_train_and_test_data(X, y)
    model.set_model()
    model.train()
    model.set_equation(idle_consumption)
    return model
