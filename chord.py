# CS410 Computers, Sound & Music
# Homework #3
# Christopher Juncker
#


import numpy as np
import scipy.io.wavfile as wf
import pyaudio

# The Assignment
#
#   Your program should be called chord — for example, chord.py if you are writing Python.
#
#
# Input
#
#   Your program should accept a chord name and a temperament name as command-line arguments.
#
#   The chord name will start with a capital letter in the range A-G, optionally followed by
#   a lowercase b to indicate that the base note is "flattened" (lowered one half-step).
#   This is the base note of the chord. Treat the base note as specifying a frequency in
#   octave 5: MIDI key numbers 72 (C) through 83 (B).
#
#   The chord name may be optionally followed by a lowercase m to indicate that the chord
#   should be minor rather than major. See above for a discussion of major and minor chords.
#
#   The temperament name will be either "equal" or "just". The just temperament used here will
#   always be based on the C scale (starts at MIDI key number 72).
#
#
# Output
#
#   Your program should create a file called chord-temperament.wav, where chord is the chord
#   name and temperament is the temperament specified on the command line. The .wav file should
#   contain single-channel 48000sps 16-bit sample data for one second of the chord. The three
#   notes of the chord should be three sine waves, each at exactly ⅙ (0.1666…) maximum amplitude:
#   samples from these notes will be added to form the output waveform.
#
#
# Example
#
#   For me, saying python3 chord.py Ebm just at the command line produced the Ebm-just.wav
#   included in the repo.
#
#
# Info
#
#   The repository http://github.com/pdx-cs-sound/hw-chord has some resources you will want for
#   this assignment. See the README there for details.
#
#



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

    # write the samples to disk
    def write(self, file="default.wav"):
        samples = self.samples.astype(np.int16)
        wf.write(file, self.sample_rate, samples)


def main():
    print("Homework 1")

    # Part 1
    #
    # Channels per frame: 1 (mono)
    # Sample size: 16 bits
    # Amplitude: ¼ maximum possible amplitude (-8192..8192)
    # Duration: one second
    # Frequency: 440Hz
    # Sample Rate: 48000 samples per second
    s = Sampler(1, 16, 0.25, 1, 440, 48000)
    s.play()
    s.write("sine2.wav")

    # Part 2
    #
    # ½ maximum amplitude (-16384..16384), except:
    # samples that would be greater than ¼ maximum amplitude (8192) should instead be ¼ maximum amplitude;
    # samples that would be less than ¼ minimum amplitude (-8192) should instead be ¼ minimum amplitude.

    # update amplitude
    # could make a new Sampler but why not re-use the old one?
    s.amplitude = 0.5
    s.generate_samples()

    # chop the top
    new_max = s.max / 4
    s.samples = np.where(s.samples <= new_max, s.samples, new_max)

    # chop the bottom
    new_min = s.min / 4
    s.samples = np.where(s.samples >= new_min, s.samples, new_min)

    s.play()
    s.write("clipped2.wav")


if __name__ == '__main__':
    main()
