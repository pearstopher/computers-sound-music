# CS410 Computers, Sound & Music
# Homework #2
# Christopher Juncker


# The Assignment
#
#   Build a program in your chosen language that will take in a a single-channel
#   WAV file at some sample rate s and produce a WAV file containing the same signal
#   at a sample rate half of s. To make my life easier, name the program halfrate —
#   for example, halfrate.py if you are writing Python.
#
#   The repository http://github.com/pdx-cs-sound/hw-resample has some resources you
#   will want for this assignment. See the README there for details.
#
#
# Filtering
#
#   For the filtering, you will need a filter. The coefficients for a good half-band
#   FIR filter with a transition bandwidth of 0.05 (5% of the maximum input frequency)
#   are provided in the repo, along with the Python code that generated those coefficients
#   in case you want to build your own. (If you want to build the filter some other way —
#   for example, an IIR filter, or some other type of FIR filter — that's fine too.)
#
#   Recall that to apply an FIR filter you convolve it with the input signal:
#
#       y[i] = Σ(j=0, N-1) a[j]x[i-j]
#
#   (Perhaps you are wondering about the indexing: FIR filters are almost always symmetric,
#   so you can take the coefficients either first-to-last or last-to-first and get the same
#   answer.)
#
#   Note that the beginning and end of the signal get a little messy: you may need to
#   prepend or append a block of N zeros. The output signal should be the same length as the
#   input signal — I'm not too fussed about how you handle the beginning and end as long as
#   this holds and the output sounds reasonable.
#
#   If you are using Python, you might want to look into the scipy.signal.lfilter() function,
#   which can process the whole signal for you really nicely rather than having to write the
#   convolution by hand.
#
#
# Testing
#
#   The files sine.wav, gc.wav and synth.wav are provided in the repo. Downsample each of these,
#   producing rsine.wav, rgc.wav and rsynth.wav respectively. Verify that the sine wave when
#   played sounds unaffected by the downsampling, and that the guitar and synth samples when
#   played sound the same up to the loss of high frequencies. (This loss is pretty subtle at half
#   rate — 48000 sps is way more than needed for most audio — so the output should sound pretty
#   much the same as the input.)


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


# class for reading Audio file
class ReadWav:
    def __init__(self, file):
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
        self.sample_rate, self.samples = wf.read(file)  # file metadata can generate WavFileWarning, ignore

        # calculate the number of channels in the wav file
        self.channels = 1 if len(self.samples.shape) == 1 else self.samples.shape[1]

        # calculate the duration of the wav file
        self.duration = self.samples.shape[0] / self.sample_rate

        # calculate the number of bits in the wav file (bit depth)
        # (scipy doesn't give the bit depth but it can be inferred from the type of np array it creates)
        if self.samples.dtype == "int16":
            self.bits = 16
        else:
            self.bits = 0  # add cases if working with other bit depths

    # play the samples with pyaudio
    def play(self):
        # this should only be used when bytes are set to 16
        # don't convert the original samples, they will be reused
        samples = self.samples.astype(np.int16)  # np.Float32, etc

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,  # paFloat32, etc
                        channels=1,
                        rate=self.sample_rate,
                        output=True)
        # https://stackoverflow.com/questions/8299303 yahweh - tobytes()
        stream.write(1 * samples.tobytes())
        stream.stop_stream()
        stream.close()
        p.terminate()




# class for holding the specifications for the audio file
class Spec:
    def __init__(self,
                 channels=1,
                 bits=16,
                 amplitude=1.0,
                 duration=1.0,
                 frequency=440,
                 sample_rate=48000,
                 ):
        self.channels = channels
        self.bits = bits
        self.amplitude = amplitude
        self.duration = duration
        self.frequency = frequency
        self.sample_rate = sample_rate


# class which creates samples based on Spec
class Sampler(Spec):
    def __init__(self, channels, bits, amplitude, duration, frequency, sample_rate):
        super().__init__(channels, bits, amplitude, duration, frequency, sample_rate)
        # set max value for current number of bits
        self.max = 2**(bits - 1) - 1
        self.min = -self.max - 1
        # generate the samples
        self.samples = None
        self.generate_samples()

    def generate_samples(self):
        self.samples = ((self.amplitude * self.max) *
                        np.sin((2*np.pi) *
                               (np.arange(self.sample_rate*self.duration)) *
                               (self.frequency/self.sample_rate)))

    # write the samples to disk
    def write(self, file="default.wav"):
        samples = self.samples.astype(np.int16)
        wf.write(file, self.sample_rate, samples)


def main():
    print("Homework 2")

    gc = ReadWav("hw2_audio/gc.wav")
    gc.play()

    # Part 1
    #
    # Channels per frame: 1 (mono)
    # Sample size: 16 bits
    # Amplitude: ¼ maximum possible amplitude (-8192..8192)
    # Duration: one second
    # Frequency: 440Hz
    # Sample Rate: 48000 samples per second
    # s = Sampler(1, 16, 0.25, 1, 440, 48000)
    # s.play()
    # s.write("sine2.wav")

    # Part 2
    #
    # ½ maximum amplitude (-16384..16384), except:
    # samples that would be greater than ¼ maximum amplitude (8192) should instead be ¼ maximum amplitude;
    # samples that would be less than ¼ minimum amplitude (-8192) should instead be ¼ minimum amplitude.

    # update amplitude
    # could make a new Sampler but why not re-use the old one?
    # s.amplitude = 0.5
    # s.generate_samples()

    # chop the top
    # new_max = s.max / 4
    # s.samples = np.where(s.samples <= new_max, s.samples, new_max)

    # chop the bottom
    # new_min = s.min / 4
    # s.samples = np.where(s.samples >= new_min, s.samples, new_min)

    # s.play()
    # s.write("clipped2.wav")


if __name__ == '__main__':
    main()
