from lib.axolotl import *
import numpy as np
from keras.models import Sequential
from keras.layers import Dense

# config
print_predictions = True

# read the data in
data = read_data("data/sample_0/accel.txt", "data/sample_0/gyro.txt")

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
print "Learning..."

# fix random seed for reproducibility
# seed = 12
# np.random.seed(seed)

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

# Fit the model
model.fit(X, Y, validation_split=0.33, nb_epoch=100, batch_size=10)

# print predictions
if print_predictions:
    for x_val, y_val in zip(X, Y):
        print y_val, ":", model.predict(np.array([x_val]), verbose=0)
