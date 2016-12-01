import numpy as np
import csv

ACCEL_TYPE = "ACCEL"
GYRO_TYPE = "GYRO"

window_len = 0.2
window_samples = 20

#
# Sets the number of samples in a window
#

def set_window_samples(n):
    global window_samples
    window_samples = n

#
# Returns a sorted stream of datum objects from the two files
#

def read_data(accel_file, gyro_file):
    data = []

    for file_path, sensor_type in [(accel_file, ACCEL_TYPE), (gyro_file, GYRO_TYPE)]:
        with open(file_path, "rb") as csvfile:
            reader = csv.DictReader(csvfile, skipinitialspace=True)
            for row in reader:
                assert row["sensor_type"] == sensor_type
                parsed_row = {
                    "touch_x": float(row["touch_x"]),
                    "touch_y": float(row["touch_y"]),
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "z": float(row["z"]),
                    "time": float(row["time_since_1970"]),
                    "type": row["sensor_type"]
                }
                data.append(parsed_row)

    data.sort(key=lambda x: x["time"])

    return data

#
# Returns a list of windows with no touching samples in the form [start, stop)
# where start and stop are indicies in the global data array
#

def get_not_touching_windows(data):
    g_time = [datum['time'] for datum in data]
    g_touch_x = [datum['touch_x'] for datum in data]

    not_touching_windows = []
    skip_to = 0
    for ii in xrange(len(g_time)):
        # skip data so windows don't overlap
        if ii < skip_to:
            continue

        # find the end of the window
        for jj in xrange(ii,len(g_time)):
            # break on touches
            if g_touch_x[jj] != -2:
                break

            # break if the window is of the correct length
            if g_time[jj] - g_time[ii] > window_len:
                not_touching_windows.append((ii, jj + 1)) # windows are of the form [start, stop)
                skip_to = jj
                break

    return not_touching_windows

#
# Returns a list of windows with touching samples in the form [start, stop)
# centered on the start of the touch where start and stop are indicies in the
# global data array. If with_labels is true, then this returns a tuple with the
# labels.
#

def get_touching_windows(data, with_labels=False):
    g_time = [datum['time'] for datum in data]
    g_touch_x = [datum['touch_x'] for datum in data]
    g_touch_y = [datum['touch_y'] for datum in data]

    # find windows where touching
    touching_points = []
    touching_labels = []
    is_touching = False
    old_touch_x = None
    old_touch_y = None
    for curr_x, curr_y, curr_time in zip(g_touch_x, g_touch_y, g_time):
        if curr_x != -2.0:
            if not is_touching:
                touching_points.append(curr_time)
                touching_labels.append([curr_x, curr_y])
                old_touch_x = curr_x
                old_touch_y = curr_y
                is_touching = True
            else:
                if old_touch_x != curr_x:
                    print old_touch_x, curr_x, curr_time
                assert old_touch_x == curr_x
                assert old_touch_y == curr_y
        else:
            is_touching = False

    # expand touching windows
    touching_window_times = [(tp - (window_len / 2), tp + (window_len / 2)) for tp in touching_points]
    touching_windows = []
    for touching_window_min, touching_window_max in touching_window_times:
        min_index = None
        max_index = None

        for ii in xrange(len(g_time)):
            if min_index is None:
                if g_time[ii] >= touching_window_min:
                    min_index = ii
            else:
                if g_time[ii] >= touching_window_max:
                    max_index = ii
                    break

        if min_index is not None and max_index is not None:
            touching_windows.append((min_index, max_index))

    if with_labels:
        return touching_windows, touching_labels
    else:
        return touching_windows

#
# Takes in an array of windows and returns all the points in the window
#

def expand_windows(data, windows, interpolated=False):
    def data_for(accel_or_gyro, start, stop):
        d = data[start:stop]
        d_for = filter(lambda x: x["type"] == accel_or_gyro, d)
        time = [datum["time"] for datum in d_for]
        x = [datum["x"] for datum in d_for]
        y = [datum["y"] for datum in d_for]
        z = [datum["z"] for datum in d_for]
        return time, x, y, z

    to_return = []

    for start, stop in windows:
        at, ax, ay, az = data_for(ACCEL_TYPE, start, stop)
        gt, gx, gy, gz = data_for(GYRO_TYPE, start, stop)
        to_return.append(
            (at, ax, ay, az, gt, gx, gy, gz)
        )

    return to_return

#
# Takes in an array of windows and returns all the points in the window,
# interpolating window samples within that
#

def expand_windows_interpolated(data, windows):
    g_time = [datum['time'] for datum in data]
    g_touch_x = [datum['touch_x'] for datum in data]
    g_touch_y = [datum['touch_y'] for datum in data]

    accel_time = [datum['time'] for datum in data if datum['type'] == ACCEL_TYPE]
    accel_x = [datum['x'] for datum in data if datum['type'] == ACCEL_TYPE]
    accel_y = [datum['y'] for datum in data if datum['type'] == ACCEL_TYPE]
    accel_z= [datum['z'] for datum in data if datum['type'] == ACCEL_TYPE]

    gyro_time = [datum['time'] for datum in data if datum['type'] == GYRO_TYPE]
    gyro_x = [datum['x'] for datum in data if datum['type'] == GYRO_TYPE]
    gyro_y = [datum['y'] for datum in data if datum['type'] == GYRO_TYPE]
    gyro_z= [datum['z'] for datum in data if datum['type'] == GYRO_TYPE]

    to_return = []

    for start, stop in windows:
        time_interp = np.linspace(g_time[start], g_time[stop], window_samples)

        to_return.append(
            (
                time_interp,
                np.interp(time_interp, accel_time, accel_x),
                np.interp(time_interp, accel_time, accel_y),
                np.interp(time_interp, accel_time, accel_z),
                time_interp,
                np.interp(time_interp, gyro_time, gyro_x),
                np.interp(time_interp, gyro_time, gyro_y),
                np.interp(time_interp, gyro_time, gyro_z)
            )
        )

    return to_return

#
# contructs feature vectors from expanded windows
#

def feature_vectors_from_windows(windows):
    to_return = []

    for at, ax, ay, az, gt, gx, gy, gz in windows:
        to_return.append(
            np.concatenate((
                ax,
                ay,
                az,
                gx,
                gy,
                gz
            ))
        )

    return to_return
