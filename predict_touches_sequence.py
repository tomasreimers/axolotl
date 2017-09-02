import sys
from lib.axolotl import *
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
import coremltools
from lib.learn_location import *
from lib.learn_touches import *

def fetch_data():
     # read the data in
    data = read_data("data/sample_0/accel.txt", "data/sample_0/gyro.txt")

    # split off the first part of data as training (the latter half will be testing)
    TRAINING_SIZE = 0.7
    slice_at = int(TRAINING_SIZE * len(data))
    train_data = data[:slice_at]
    test_data = data[slice_at:]
    return train_data, test_data

def graph_predictions(model, test_data):
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

def export_coreml_location_model(model):
    cm = coremltools.converters.keras.convert(
        model, input_names=['accel_gyro_stream'], output_names=['touch_predictions'])
    cm.author = 'Tomas Reimers & Greg Foster'
    cm.license = 'MIT'
    cm.short_description = ''
    cm.input_description['accel_gyro_stream'] = 'An array of time indexed sensor data'
    cm.output_description['touch_predictions'] = 'Was the screen touched or not?'
    cm.save('location_model.mlmodel')

def export_coreml_touch_model(model):
    cm = coremltools.converters.keras.convert(
        model, input_names=['touch_windows'], output_names=['touch_predictions'])
    cm.author = 'Tomas Reimers & Greg Foster'
    cm.license = 'MIT'
    cm.short_description = ''
    cm.input_description['touch_windows'] = 'An array of arrays of time indexed sensor data'
    cm.output_description['touch_predictions'] = 'Where was the screen touched?'
    cm.save('touch_model.mlmodel')

if __name__ == "__main__":
    train_data, test_data = fetch_data()
    argc = len(sys.argv)
    if argc == 2 and sys.argv[1] == 'plot':
        model = train_touch_model(train_data)
        graph_predictions(model, test_data)
    elif argc == 2 and sys.argv[1] == 'coreml':
        # Use all data, no point in eval when training for export.
        print('training touch model')
        model = train_touch_model(train_data + test_data)
        export_coreml_touch_model(model)
        print('saved touch model')
        print('training location model')
        model = train_location_model(train_data + test_data)
        export_coreml_location_model(model)
        print('saved location model')
