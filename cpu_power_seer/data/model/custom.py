from cpu_power_seer.data.model.model import Model
from cpu_power_seer.logs.logger import log


class CustomModel(Model):

    # Comment this method or modify it if you want to add new attributes to your custom model
    def __init__(self, name):
        log("Empty custom class", "ERR")
        log("Implement custom class to use custom prediction method", "ERR")
        exit(1)
        super().__init__(name)
