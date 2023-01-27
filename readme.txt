
# example: granulate sample.wav into 100 ms granulations.
python granulate.py sample.wav 100

# example: granulate sample.wav into 25 ms granulations.
python granulate.py sample.wav 25

# notes
Fade is done automatically using ffmpeg linear fade with duration of 1/10 of the granule size on fade in and fade out.


