from lib.axolotl import *
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split

# read the data in
data = read_data("data/sample_0/accel.txt", "data/sample_0/gyro.txt")

# split off the first part of data as training (the latter half will be testing)
TRAINING_SIZE = 0.7
slice_at = int(TRAINING_SIZE * len(data))
train_data = data[:slice_at]
test_data = data[slice_at:]

# find windows where not touching
not_touching_windows = get_not_touching_windows(train_data)
expanded_not_touching_windows = expand_windows_interpolated(train_data, not_touching_windows)

# find windows where touching
touching_windows = get_touching_windows(train_data)
expanded_touching_windows = expand_windows_interpolated(train_data, touching_windows)

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

# generate windows every 10ms for time in prediction
windows = get_all_windows(test_data, min_start_distance=0.01)
expanded_windows = expand_windows_interpolated(test_data, windows)
feature_vectors = feature_vectors_from_windows(expanded_windows)

# predict the touches
pred = model.predict(np.array(feature_vectors))

# graph the raw data
g_time = [datum['time'] for datum in test_data]
g_touch_x = [datum['touch_x'] for datum in test_data]
g_touch_y = [datum['touch_y'] for datum in test_data]

accel_time = [datum['time'] for datum in test_data if datum['type'] == ACCEL_TYPE]
accel_x = [datum['x'] for datum in test_data if datum['type'] == ACCEL_TYPE]
accel_y = [datum['y'] for datum in test_data if datum['type'] == ACCEL_TYPE]
accel_z= [datum['z'] for datum in test_data if datum['type'] == ACCEL_TYPE]

gyro_time = [datum['time'] for datum in test_data if datum['type'] == GYRO_TYPE]
gyro_x = [datum['x'] for datum in test_data if datum['type'] == GYRO_TYPE]
gyro_y = [datum['y'] for datum in test_data if datum['type'] == GYRO_TYPE]
gyro_z= [datum['z'] for datum in test_data if datum['type'] == GYRO_TYPE]

plt.subplot(2, 1, 1)

ax_h, = plt.plot(accel_time, accel_x, label="Accel X")
ay_h, = plt.plot(accel_time, accel_y, label="Accel Y")
az_h, = plt.plot(accel_time, accel_z, label="Accel Z")

gx_h, = plt.plot(gyro_time, gyro_x, label="Gyro X")
gy_h, = plt.plot(gyro_time, gyro_y, label="Gyro Y")
gz_h, = plt.plot(gyro_time, gyro_z, label="Gyro Z")

plt.legend(handles=[ax_h, ay_h, az_h, gx_h, gy_h, gz_h])

first_touch = None
last_touch = None
for curr_x, curr_time in zip(g_touch_x, g_time):
    if curr_x != -2.0:
        if first_touch is None:
            first_touch = curr_time
        last_touch = curr_time
    else:
        if first_touch is not None:
            plt.axvspan(first_touch, last_touch, color='red', alpha=0.25)
            first_touch = None
            last_touch = None

plt.subplot(2, 1, 2)

plt.plot([(g_time[window[0]] + g_time[window[1] - 1]) / 2 for window in windows], pred)

first_touch = None
last_touch = None
for curr_x, curr_time in zip(g_touch_x, g_time):
    if curr_x != -2.0:
        if first_touch is None:
            first_touch = curr_time
        last_touch = curr_time
    else:
        if first_touch is not None:
            plt.axvspan(first_touch, last_touch, color='red', alpha=0.25)
            first_touch = None
            last_touch = None

plt.show()
