from lib.axolotl import *
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split

# config
print_predictions = False

def train_touch_model(data):
    # find windows where not touching
    not_touching_windows = get_not_touching_windows(data)
    expanded_not_touching_windows = expand_windows_interpolated(data, not_touching_windows)

    # find windows where touching
    touching_windows = get_touching_windows(data)
    expanded_touching_windows = expand_windows_interpolated(data, touching_windows)

    # convert to feature vectors
    positive_feature_vectors = feature_vectors_from_windows(expanded_touching_windows)
    negative_feature_vectors = feature_vectors_from_windows(expanded_not_touching_windows)

    # split into input (X) and output (Y) variables
    X = np.array(map(np.array, positive_feature_vectors) + map(np.array, negative_feature_vectors))
    Y = np.array([1] * len(positive_feature_vectors) + [0] * len(negative_feature_vectors))

    # create model
    model = Sequential()
    model.add(Dense(window_samples * 4, input_dim=window_samples * 6, activation='relu'))
    model.add(Dense(window_samples * 2, activation='relu'))
    model.add(Dense(window_samples, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(X, Y, nb_epoch=40, batch_size=20)
    return model

def learn_touches(accel_file, gyro_file, verbose=True):
    # read the data in
    data = read_data(accel_file, gyro_file)

    # find windows where not touching
    not_touching_windows = get_not_touching_windows(data)
    expanded_not_touching_windows = expand_windows_interpolated(data, not_touching_windows)

    # find windows where touching
    touching_windows = get_touching_windows(data)
    expanded_touching_windows = expand_windows_interpolated(data, touching_windows)

    # convert to feature vectors
    positive_feature_vectors = feature_vectors_from_windows(expanded_touching_windows)
    negative_feature_vectors = feature_vectors_from_windows(expanded_not_touching_windows)

    # learn
    if verbose:
        print "Learning..."

    # fix random seed for reproducibility
    # seed = 12
    # np.random.seed(seed)

    # split into input (X) and output (Y) variables
    X = np.array(map(np.array, positive_feature_vectors) + map(np.array, negative_feature_vectors))
    Y = np.array([1] * len(positive_feature_vectors) + [0] * len(negative_feature_vectors))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33)

    # create model
    model = Sequential()
    model.add(Dense(window_samples * 4, input_dim=window_samples * 6, activation='relu'))
    model.add(Dense(window_samples * 2, activation='relu'))
    model.add(Dense(window_samples, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Fit the model
    verbosity = 0
    if verbose:
        verbosity = 1
    model.fit(X_train, Y_train, validation_data=(X_test, Y_test), nb_epoch=40, batch_size=20, verbose=verbosity)

    # print predictions
    if print_predictions and verbose:
        for x_val, y_val in zip(X_test, Y_test):
            print y_val, ":", model.predict(np.array([x_val]), verbose=0)

    return dict(zip(model.metrics_names, model.evaluate(X_test, Y_test, verbose=verbosity)))

if __name__ == "__main__":
    learn_touches("data/sample_0/accel.txt", "data/sample_0/gyro.txt")
    print ""
