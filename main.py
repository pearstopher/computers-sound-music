# CS410 Computers, Sound & Music
#
# Playing with Fourier transform
#
# Christopher Juncker

import numpy as np
import scipy.io.wavfile as wf
import scipy.signal as signal
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

        # you can add in an overtone to make this more exciting
        # overtone = ((self.amplitude / 1.25 * self.max) *
        #  np.sin((2 * np.pi) *
        #         (np.arange(self.sample_rate * self.duration)) *
        #         (self.frequency * 2 / self.sample_rate)))
        #
        # self.samples += overtone

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
        stream.write(1 * samples.tobytes())
        stream.stop_stream()
        stream.close()
        p.terminate()

    # write the samples to disk
    def write(self, file="default.wav"):
        samples = self.samples.astype(np.int16)
        wf.write(file, self.sample_rate, samples)


# utility function: print a spectrogram from the STFT
def spectrogram(f, t, zxx):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.istft.html
    plt.figure()
    plt.pcolormesh(t, f, np.abs(zxx), vmin=0, vmax=8192, shading='gouraud')  # 8192 = max sin amplitude
    # plt.ylim([f[1], f[-1]])  # this shows the whole range of possible frequencies
    plt.ylim(400,1000)  # this narrows down on the frequencies I am making (440 and optionally 880 hz)
    plt.title('STFT Magnitude')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.yscale('log')
    plt.show()


# utility function: print a graph of the sine waves before and after
def graph_sines(old_samples, new_samples):
    periods = 4  # how many periods of the original sine wave to display
    plt.plot(old_samples[0:int(48000 / 440 * periods)])
    plt.plot(new_samples[0:int(48000 / 440 * periods)])
    plt.xlabel("1/48000 s")
    plt.ylabel("amplitude")
    plt.show()


def main():
    # create and play sound wave
    # 440 hz
    s = Sampler(1, 16, 0.25, 1, 440, 48000)
    s.play()

    # apply Short Time Fourier Transform (STFT) to samples
    fs = 48000
    f, t, zxx = signal.stft(s.samples, fs=fs, nperseg=fs/2)

    # apply Inverse Short Time Fourier Transform (ISTFT) to re-create samples
    old_samples = np.copy(s.samples)
    _, new_samples = signal.istft(zxx, fs)
    s.samples = np.copy(new_samples)

    # play the reconstructed sin wave
    s.play()

    # display the spectrogram of the original frequencies
    # spectrogram(f, t, zxx)

    # display the first few periods of the sin wave alongside its reconstruction
    graph_sines(old_samples, new_samples)
    # you can see that the new wave (yellow) is oscillating slower than the original (blue)
    # this is because its frequency is now slightly lower


if __name__ == '__main__':
    main()
