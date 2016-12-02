# Axolotl

## About

Axolotl is a library that attempts to discern user screen taps from the
motion of the accelerometer and gyroscope.

Key files:

 - `visualize.py`: This visualizes the data in various ways, because *data
 science is important*.
 - `learn_touches.py`: This learns what samples are touches.
 - `learn_location.py`: This learns the location for samples of touches.
 - `stats.py`: Runs both learn_touches and learn_location on all samples and
 reports statistics.

This can all be run with python with the current working directory set to the
root directory of this repository.

## Authors

(c) Tomas Reimers, Greg Foster 2016
