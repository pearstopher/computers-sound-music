# CS410 Computers, Sound & Music
#
# Playing with Fourier transform
#
# Christopher Juncker

import numpy as np
import scipy.io.wavfile as wf
import pyaudio
import matplotlib.pyplot as plt


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

    # create a440hz sin wave with duration 1s
    s = Sampler(1, 16, 0.25, 1, 440, 48000)
    s.play()


    # display the first two periods of the sin wave
    plt.plot(s.samples[0:int(48000/440*2)])
    plt.xlabel("1/48000 s")
    plt.ylabel("amplitude")
    plt.show()



    # apply Short Time Fourier Transform (STFT) to samples





    # apply Inverse Short Time Fourier Transform (ISTFT) to samples



if __name__ == '__main__':
    main()
