# CS410 Computers, Sound & Music
# Homework #1
# Christopher Juncker
#

import wave
# INSTALLING/IMPORTING sounddevice:
#   (sounddevice was suggested as a simpler alternative to pyaudio)
#   >pip install sounddevice
#   import sounddevice
#
# INSTALLING/IMPORTING pyaudio:
#   suggestion to install visual c++ before installing pyaudio
#   https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
#
#   the above didn't work so I tried installing a 'wheel' for my version of python here:
#   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
#   then I `pip install The_file_I_downloaded.whl`
#   (source: https://stackoverflow.com/questions/59467023)
import pyaudio

import numpy as np

# example of writing a .wav file with scipy
# https://stackoverflow.com/questions/52477889
import scipy.io.wavfile as wf


# The Assignment
#
#   1.  Build a program in your chosen language that writes a sine wave to a WAV file named sine.wav
#       in the current directory. Specifications for your sine wave:
#
#           Channels per frame: 1 (mono)
#           Sample size: 16 bits
#           Amplitude: ¼ maximum possible amplitude (-8192..8192)
#           Duration: one second
#           Frequency: 440Hz
#           Sample Rate: 48000 samples per second
#
#       Generate the samples yourself using your language's sin() function — if your language has no
#       math library, get a different language.
#
#   2.  Extend your program to also write a WAV file named clipped.wav in the current directory.
#       Generate a sine wave as though it were ½ maximum amplitude (-16384..16384), except: samples
#       that would be greater than ¼ maximum amplitude (8192) should instead be ¼ maximum amplitude;
#       samples that would be less than ¼ minimum amplitude (-8192) should instead be ¼ minimum
#       amplitude. Other than this change, all other parameters remain the same as in Part 1.
#
#       Your wave should look "clipped" like this in Audacity. Note the phase: the waveform starts
#       upward from zero.
#
#       Also check the sample rate, amplitude and frequency while you're in Audacity. On Linux the
#       file command will also tell you the frequency, number of channels, and bits per sample. Or
#       you can use the wavfile Python utility I built for the course. Lots of options.
#
#   3.  Extend your program to also play the same clipped sine wave on your computer's audio output.
#       Do not shell out to an external program for this: use an audio library.
#
#       Each time your program is run, it should do all three of these things.
#

p = pyaudio.PyAudio()

# specifications for my file
#
# writes a sine wave to a WAV file named sine.wav in the current directory
FILE = "./sine.wav"
# Channels per frame: 1 (mono)
CHANNELS = 1
# Sample size: 16 bits
BITS = 16
# Amplitude: ¼ maximum possible amplitude (-8192..8192)
AMP = -4096
# Duration: one second
DURATION = 1
# Frequency: 440Hz
FREQ = 440
# Sample Rate: 48000 samples per second
RATE = 48000


# nice help with tobytes() from yahweh
# https://stackoverflow.com/questions/8299303
samples = (np.sin(2*np.pi*np.arange(RATE*DURATION)*FREQ/RATE)).astype(np.float32)

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=RATE,
                output=True)

# play the file
stream.write(1*samples.tobytes())
stream.stop_stream()
stream.close()
p.terminate()


# write the file
wf.write(FILE, RATE, samples)


def main():
    print("Homework 1")


if __name__ == '__main__':
    main()
