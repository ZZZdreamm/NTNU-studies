import numpy as np


def func(X: np.ndarray) -> np.ndarray:
    """
    The data generating function.
    Do not modify this function.
    """
    return 0.3 * X[:, 0] + 0.6 * X[:, 1] ** 2


def noisy_func(X: np.ndarray, epsilon: float = 0.075) -> np.ndarray:
    """
    Add Gaussian noise to the data generating function.
    Do not modify this function.
    """
    return func(X) + np.random.randn(len(X)) * epsilon


def get_data(n_train: int, n_test: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Generating training and test data for
    training and testing the neural network.
    Do not modify this function.
    """
    X_train = np.random.rand(n_train, 2) * 2 - 1
    y_train = noisy_func(X_train)
    X_test = np.random.rand(n_test, 2) * 2 - 1
    y_test = noisy_func(X_test)

    return X_train, y_train, X_test, y_test


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """ Initializes the network's layers and their weights and biases. """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.weights_hidden = np.random.rand(input_size, hidden_size)
        self.bias_hidden = np.random.rand(hidden_size)

        self.weights_output = np.random.rand(hidden_size, output_size)
        self.bias_output = np.random.rand(output_size)

    def sigmoid(self, x):
        """ Computes the sigmoid function for a given x. """
        return 1 / (1 + np.exp(-x))

    def forward(self, X):
        """ Performes the forward pass through the network. """
        self.x_weights_hidden = np.dot(X, self.weights_hidden) + self.bias_hidden
        self.after_activation_hidden = self.sigmoid(self.x_weights_hidden)

        self.x_weights_output = np.dot(self.after_activation_hidden, self.weights_output) + self.bias_output
        self.after_activation_output = self.x_weights_output

        return self.after_activation_output

    def compute_loss(self, Y_pred, Y_true):
        """ Computes the Mean Squared Error loss """
        return np.mean(np.square(Y_true - Y_pred))

    def backward(self, X, y):
        """ Performes the backward propagation through the network. """
        y = y.reshape(-1, 1)
        output_error = self.after_activation_output - y

        hidden_output_error = np.dot(output_error, self.weights_output.T)
        sigmoid_derivative = self.after_activation_hidden[:, 1:] * (1 - self.after_activation_hidden[:, 1:])
        hidden_error = hidden_output_error * sigmoid_derivative

        hidden_pd = X * hidden_error
        output_pd = self.after_activation_hidden * output_error

        total_hidden_gradient = np.average(hidden_pd, axis=0)
        total_output_gradient = np.average(output_pd, axis=0)

        return total_hidden_gradient, total_output_gradient

    def train(self, X_train, Y_train, num_epochs, learning_rate):
        """ Trains the network through a given number of epochs. """
        avarage_loss = 0
        for epoch in range(num_epochs):
            Y_pred = self.forward(X_train)
            loss = self.compute_loss(Y_pred, Y_train)
            avarage_loss += loss

            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Loss: {loss}')

            total_hidden_gradient, total_output_gradient = self.backward(X_train, Y_train)

            self.weights_hidden -= learning_rate * total_hidden_gradient
            self.weights_output -= learning_rate * total_output_gradient.reshape(-1, 1)
        return avarage_loss


if __name__ == "__main__":
    np.random.seed(0)
    X_train, y_train, X_test, y_test = get_data(n_train=280, n_test=120)
    network = NeuralNetwork(2, 2, 1)
    epochs_number = 100
    learning_rate = 0.1
    print(f'Learning rate: {learning_rate}')
    print(f'Number of epochs: {epochs_number}')
    avarage_loss_train = network.train(X_train, y_train, epochs_number, learning_rate) / epochs_number
    print(f'Average Train: {avarage_loss_train}\n')
    avarage_loss_test = network.train(X_test, y_test, epochs_number, learning_rate) / epochs_number
    print(f'Average Test: {avarage_loss_test}')
