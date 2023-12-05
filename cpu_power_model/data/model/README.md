# Model
Python module to implement CPU power models. To implement new models, create a class that inherits from Model (model.py) and implements the following methods:

- **set_train_and_test_data(self, X, y)**: Format X and Y to fits your model. Then assign the values you finally obtain to self.X_train, self.y_train, self.X_test = X_test and self.y_test.
- **set_actual_values(self, X, y)**: Set actual values in the same format as training and test values.
- **set_model(self)**: Create an instance of the model type you want to use and assign it to self.model.
- [Optional] **set_equation(self, idle_consumption)**: Set a string representing the equation of your model (if exists).

You can overwrite the other methods if necessary.