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


import sys
import numpy as np
import scipy.io.wavfile as wf
from scipy import signal


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

    # write the samples to disk
    def write(self, file="default.wav"):
        wf.write(file, self.sample_rate, self.samples)

    # resample with simple filter
    def simple_halfrate_filter(self):
        new_samples = np.empty(int(len(self.samples) / 2), dtype="int16")
        for i in range(len(new_samples)):
            # special case for first element so I don't try to access index -1
            if i == 0:
                new_samples[i] = self.samples[i*2]
            else:
                new_samples[i] = int((self.samples[i*2] + self.samples[i*2 - 1]) / 2)

        self.samples = new_samples
        self.sample_rate = int(self.sample_rate/2)

    # resample with "a good half-band FIR filter with a transition bandwidth of 0.05"
    # https://github.com/pdx-cs-sound/hw-resample
    def better_halfrate_filter(self):
        # this generates the filter window parameters
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.kaiserord.html
        #
        # Parameters:
        #   ripple: -40 = upper bound for deviation between Desired and Actual frequency response
        #   width: 0.05 = width of transition band, expressed as a fraction of nyquist frequency
        #
        # Return values:
        #   numtaps = length of window, number of samples
        #   beta = number which determines window shape
        #       (often expressed as "alpha", where beta = pi * alpha)
        numtaps, beta = signal.kaiserord(-40, 0.05)

        # this accepts the window parameters and generates the array of coefficients
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html
        #
        # cutoff: 0.45 = the cutoff frequency.
        #   0.45 = 0.5 max frequency - 0.05 transition band
        #
        # scale: True = ??? I don't understand the scale argument yet. What is "unity"?
        subband = signal.firwin(numtaps, 0.45, window=('kaiser', beta), scale=True)

        # "Even if you are using Python, please write the convolution code by hand for this assignment"
        #
        # 1. Create an new array of half the size
        new_samples = np.zeros(int(len(self.samples) / 2), dtype="float64")
        # 2. Loop through the new array to fill it (looping through the original would be twice as much work)
        for i in range(len(new_samples)):
            # 3. Loop through the coefficients
            for j, coefficient in enumerate(subband):
                # 4. Convolve the original samples with the subband
                # "- int(len(subband) / 2))" shifts the subband so that it is centered on the current sample
                if 0 <= (i * 2 + j - int(len(subband) / 2)) < len(self.samples):
                    new_samples[i] += self.samples[i * 2 + j - int(len(subband) / 2)] * coefficient
                # 5. Simply ignore if the index is out of range to simulate padding with 0s
        self.samples = new_samples
        self.samples = self.samples.astype("int16")

        # np.convolve and signal.convolve do this so much faster <3 <3 <3
        # self.samples = signal.convolve(self.samples, subband)
        # self.samples = self.samples.astype("int16")  # lost my int16s
        # self.samples = self.samples[0::2]

        # can also loop faster using np.dot in the inner loop
        # (new_samples = half the size of the original sample array)
        # s = len(subband)
        # for i in range(len(new_samples) - s):
        #     new_samples[i] = np.dot(self.samples[i*2:i*2+s], subband)

        self.sample_rate = int(self.sample_rate/2)


def main():
    print("Homework 2")

    # run with any number of command line arguments:
    #   halfrate.py gc.wav
    #   halfrate.py gc.wav sine.wav synth.wav
    #   etc
    for file in sys.argv[1:]:
        # reads from and writes to the current directory
        samples = ReadWav(file)
        samples.better_halfrate_filter()
        samples.write("r" + file)


if __name__ == '__main__':
    main()
