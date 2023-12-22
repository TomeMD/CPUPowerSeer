from cpu_power_model.config import config
from cpu_power_model.data.process import get_idle_consumption, get_formatted_vars
from cpu_power_model.data.model import PolynomialModel, FreqWoInteractionTerms, PerceptronModel, CustomModel


def run(train_timestamps, time_series):
    model = None
    if config.prediction_method == "polynomial":
        model = PolynomialModel(config.model_name)
    elif config.prediction_method == "freqwointeractionterms":
        model = FreqWoInteractionTerms(config.model_name)
    elif config.prediction_method == "perceptron":
        model = PerceptronModel(config.model_name)
    elif config.prediction_method == "custom":
        model = CustomModel(config.model_name)

    idle_consumption = get_idle_consumption(train_timestamps, config.train_range)
    X, y = get_formatted_vars(config.x_vars, time_series)

    model.set_train_and_test_data(X, y)
    model.set_model()
    model.train()
    model.set_equation(idle_consumption)

    return model
