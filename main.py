# CS410 Computers, Sound & Music
# Homework #1
# Christopher Juncker
#

import numpy as np

# wave was suggested but I am exploring alternatives like scipy
# import wave
#
# example of writing a .wav file with scipy
# https://stackoverflow.com/questions/52477889
import scipy.io.wavfile as wf


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


# class for holding the specifications for the audio file
class Spec:
    def __init__(self,
                 file="default.wav",
                 channels=1,
                 bits=16,
                 amplitude=1.0,
                 duration=1.0,
                 frequency=440,
                 sample_rate=48000,
                 ):
        self.file = file
        self.channels = channels
        self.bits = bits
        self.amplitude = amplitude
        self.duration = duration
        self.frequency = frequency
        self.sample_rate = sample_rate


# class for creating a sample based on given specifications
def sample(spec):
    amp_max = 2**spec.bits - 1
    samples = ((spec.amplitude * amp_max) *
               np.sin((2*np.pi) *
                      (np.arange(spec.sample_rate*spec.duration))
                      * (spec.frequency/spec.sample_rate)))

    return samples


def main():
    print("Homework 1")

    specs = Spec("sine.wav", 1, 16, 0.5, 1, 440, 48000)
    samples = sample(specs)

    # chop the top
    samples = np.where(samples <= (32767 * (specs.amplitude / 2)),
                       samples,
                       (32767 * (specs.amplitude / 2)))
    # chop the bottom
    # chop the top
    samples = np.where(samples >= -(32767 * (specs.amplitude / 2)),
                       samples,
                       -(32767 * (specs.amplitude / 2)))

    samples = samples.astype(np.int16)  # np.Float32

    p = pyaudio.PyAudio()
    # stream = p.open(format=pyaudio.paFloat32,
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=specs.sample_rate,
                    output=True)

    # play the file
    stream.write(1 * samples.tobytes())  # https://stackoverflow.com/questions/8299303 yahweh - tobytes()
    stream.stop_stream()
    stream.close()
    p.terminate()

    # write the file
    wf.write(specs.file, specs.sample_rate, samples)


if __name__ == '__main__':
    main()
