import matplotlib.pyplot as plt
from lib.axolotl import *

PHASE_0_RAW_DATA = 0
PHASE_1_RAW_DATA = 1
PHASE_2_WINDOWS = 2
PHASE_3_SAMPLES = 3
PHASE_4_INTERP_10_SAMPLES = 4
PHASE_5_INTERP_20_SAMPLES = 5
PHASE_6_INTERP_30_SAMPLES = 6

# read the data in
data = read_data("data/sample_0/accel.txt", "data/sample_0/gyro.txt")

# find windows where not touching
not_touching_windows = get_not_touching_windows(data)

# find windows where touching
touching_windows = get_touching_windows(data)

# graph the windows
phase = None
options = {
    "Raw Data": PHASE_0_RAW_DATA,
    "Raw Data with Touches": PHASE_1_RAW_DATA,
    "Windows": PHASE_2_WINDOWS,
    "Samples": PHASE_3_SAMPLES,
    "Samples (interpolated, 10 points)": PHASE_4_INTERP_10_SAMPLES,
    "Samples (interpolated, 20 points)": PHASE_5_INTERP_20_SAMPLES,
    "Samples (interpolated, 30 points)": PHASE_6_INTERP_30_SAMPLES,
}
while phase not in options.values():
    for k, v in sorted(options.iteritems(), key=lambda x: x[1]):
        print "Option " + str(v) + ": " + k
    phase = int(raw_input("Which option would you like to visualize (number only): "))

if PHASE_4_INTERP_10_SAMPLES == phase:
    set_window_samples(10)
if PHASE_5_INTERP_20_SAMPLES == phase:
    set_window_samples(20)
if PHASE_6_INTERP_30_SAMPLES == phase:
    set_window_samples(30)

if phase in [PHASE_0_RAW_DATA, PHASE_1_RAW_DATA, PHASE_2_WINDOWS]:
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

    ax_h, = plt.plot(accel_time, accel_x, label="Accel X")
    ay_h, = plt.plot(accel_time, accel_y, label="Accel Y")
    az_h, = plt.plot(accel_time, accel_z, label="Accel Z")

    gx_h, = plt.plot(gyro_time, gyro_x, label="Gyro X")
    gy_h, = plt.plot(gyro_time, gyro_y, label="Gyro Y")
    gz_h, = plt.plot(gyro_time, gyro_z, label="Gyro Z")

    plt.legend(handles=[ax_h, ay_h, az_h, gx_h, gy_h, gz_h])

    # graph times when touching
    first_touch = None
    last_touch = None

    if phase != PHASE_0_RAW_DATA:
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

    if phase == PHASE_2_WINDOWS:
        # graph touching windows
        for touch_start, touch_end in touching_windows:
            plt.axvspan(g_time[touch_start], g_time[touch_end], color='blue', alpha=0.25)

        # graph not touching windows
        for touch_start, touch_end in not_touching_windows:
            plt.axvspan(g_time[touch_start], g_time[touch_end], color='green', alpha=0.25)

    # show the plot
    plt.show()

if phase in [PHASE_3_SAMPLES, PHASE_4_INTERP_10_SAMPLES, PHASE_5_INTERP_20_SAMPLES, PHASE_6_INTERP_30_SAMPLES]:
    # settings
    m = 10
    n = 10
    min_y = -1
    max_y = 1

    # graph
    for windows, title in [(touching_windows, "Touching Samples"), (not_touching_windows, "Resting Samples")]:
        print title

        if phase == PHASE_3_SAMPLES:
            expanded_windows = expand_windows(data, windows)
        else:
            expanded_windows = expand_windows_interpolated(data, windows)

        for ii in xrange(min(len(expanded_windows), m * n)):
            at, ax, ay, az, gt, gx, gy, gz = expanded_windows[ii]

            curr_plot = plt.subplot(m, n, ii + 1) # the position parameter is 1-indexed

            plt.plot(at, ax)
            plt.plot(at, ay)
            plt.plot(at, az)

            plt.plot(gt, gx)
            plt.plot(gt, gy)
            plt.plot(gt, gz)

            curr_plot.xaxis.set_visible(False)
            curr_plot.yaxis.set_visible(False)

            plt.ylim(min_y, max_y)

        plt.show()
