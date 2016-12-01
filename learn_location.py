from lib.axolotl import *
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense

# config
print_predictions = True
graph_predictions = True

# read the data in
data = read_data("data/sample_0/accel.txt", "data/sample_0/gyro.txt")

# find windows where touching
touching_windows, touching_labels = get_touching_windows(data, with_labels=True)
expanded_touching_windows = expand_windows_interpolated(data, touching_windows)

# convert to feature vectors
positive_feature_vectors = feature_vectors_from_windows(expanded_touching_windows)

# learn

# fix random seed for reproducibility
# seed = 12
# np.random.seed(seed)

# split into input (X) and output (Y) variables
X = np.array(map(np.array, positive_feature_vectors))
Y = np.array(map(np.array, touching_labels))

# create model
model = Sequential()
model.add(Dense(window_samples * 4, input_dim=window_samples * 6, activation='linear'))
model.add(Dense(window_samples * 2, activation='linear'))
model.add(Dense(window_samples, activation='linear'))
model.add(Dense(2, activation='linear'))

# Compile model
model.compile(loss='mse', optimizer='adam', metrics=['mse'])

# Fit the model
model.fit(X, Y, validation_split=0.33, nb_epoch=150, batch_size=10)

# print predictions
if print_predictions:
    for x_val, y_val in zip(X, Y):
        print y_val, ":", model.predict(np.array([x_val]), verbose=0)

# graph predictions
if graph_predictions:
    m = 10
    n = 10

    pred_data = zip(X, Y)

    for ii in xrange(min(m * n, len(X))):
        x_val, y_val = pred_data[ii]

        curr_plot = plt.subplot(m, n, ii + 1) # the position parameter is 1-indexed

        plt.plot(y_val[0], y_val[1], 'go')
        pred = model.predict(np.array([x_val]), verbose=0).flatten()
        plt.plot(pred[0], pred[1], 'ro')

        curr_plot.xaxis.set_visible(False)
        curr_plot.yaxis.set_visible(False)

        plt.ylim(-1, 1)
        plt.xlim(-1, 1)

    plt.show()
