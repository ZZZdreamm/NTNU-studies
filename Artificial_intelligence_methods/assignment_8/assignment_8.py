import pickle
from typing import Dict, List, Any, Union
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences


def load_data() -> Dict[str, Union[List[Any], int]]:
    path = "keras-data.pickle"
    with open(file=path, mode="rb") as file:
        data = pickle.load(file)

    return data


def preprocess_data(data: Dict[str, Union[List[Any], int]]) -> Dict[str, Union[List[Any], np.ndarray, int]]:
    maxlen = data["max_length"] // 16
    data["x_train"] = pad_sequences(data['x_train'], maxlen=maxlen)
    data["y_train"] = np.asarray(data['y_train'])
    data["x_test"] = pad_sequences(data['x_test'], maxlen=maxlen)
    data["y_test"] = np.asarray(data['y_test'])

    return data


def build_feedforward_model(input_dim: int, maxlen: int) -> tf.keras.Sequential:
    """ Builds feedforward network."""
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=input_dim, output_dim=128))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(128, activation='relu'))
    model.add(tf.keras.layers.Dense(128, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    return model


def build_recurrent_model(input_dim: int, maxlen: int) -> tf.keras.Sequential:
    """ Builds recurrent network."""
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=input_dim, output_dim=128))
    model.add(tf.keras.layers.LSTM(128))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    return model


def train_model(data: Dict[str, Union[List[Any], np.ndarray, int]], model_type="feedforward") -> float:
    """ Trains the model. """
    x_train, y_train = data["x_train"], data["y_train"]
    x_test, y_test = data["x_test"], data["y_test"]
    input_dim = np.max(np.concatenate((x_train, x_test))) + 1
    maxlen = x_train.shape[1]

    if model_type == "feedforward":
        model = build_feedforward_model(input_dim, maxlen)
    elif model_type == "recurrent":
        model = build_recurrent_model(input_dim, maxlen)

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=2, batch_size=128, validation_split=0.1)
    _, test_accuracy = model.evaluate(x_test, y_test)
    return test_accuracy


def main() -> None:
    print("1. Loading data...")
    keras_data = load_data()
    print("2. Preprocessing data...")
    keras_data = preprocess_data(keras_data)
    print("3. Training feedforward neural network...")
    fnn_test_accuracy = train_model(keras_data, model_type="feedforward")
    print('Model: Feedforward NN.\n'
          f'Test accuracy: {fnn_test_accuracy:.3f}')
    print("4. Training recurrent neural network...")
    rnn_test_accuracy = train_model(keras_data, model_type="recurrent")
    print('Model: Recurrent NN.\n'
          f'Test accuracy: {rnn_test_accuracy:.3f}')


if __name__ == '__main__':
    main()
