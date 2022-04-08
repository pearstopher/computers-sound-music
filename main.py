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
class Samples:
    def __init__(self):
        # I could generate these, but I know them
        self.channels = 1
        self.bits = 16
        self.sample_rate = 48000

        self.max = 2**(self.bits - 1) - 1
        self.min = -self.max

        # load the two tracks
        _, self.track_1 = wf.read("frequency_guitar.wav")
        self.track_1 = np.array(self.track_1, dtype=np.int16)
        _, self.track_2 = wf.read("frequency_vocal.wav")
        self.track_2 = np.array(self.track_2, dtype=np.int16)

        # combine tracks by cutting amplitude in half and adding together
        self.master = (self.track_1 / 2) + (self.track_2 / 2)

    # play the samples with pyaudio
    def play(self):
        # this should only be used when bytes are set to 16
        # don't convert the original samples, they will be reused
        samples = self.master.astype(np.int16)  # np.Float32, etc

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
        samples = self.master.astype(np.int16)
        wf.write(file, self.sample_rate, samples)


# utility function: print a spectrogram from the STFT
def spectrogram(f, t, zxx):
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.istft.html
    plt.figure()
    plt.pcolormesh(t, f, np.abs(zxx), vmin=0, vmax=8192, shading='gouraud')  # 8192 = max sin amplitude
    # plt.ylim([f[1], f[-1]])  # this shows the whole range of possible frequencies
    plt.ylim(400, 1000)  # this narrows down on the frequencies I am making (440 and optionally 880 hz)
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
    # play unmodified audio tracks
    s = Samples()
    s.play()

    # apply Short Time Fourier Transform (STFT) to samples
    fs = 48000
    f, t, zxx = signal.stft(s.master, fs=fs, nperseg=fs/2)

    # shift all the frequencies up(+) or down(-) by a random amount
    shift = -30
    zxx = np.roll(zxx, shift, axis=0)  # axis 0 = time, axis 1 = frequency
    # zero out the elements that roll over/under
    if shift > 0:
        zxx[0:shift] = 0
    else:
        zxx[shift:0] = 0

    # apply Inverse Short Time Fourier Transform (ISTFT) to re-create samples
    old_samples = np.copy(s.master)
    _, new_samples = signal.istft(zxx, fs)
    s.master = np.copy(new_samples)

    # play the reconstructed sin wave
    s.play()

    # display the spectrogram of the original frequencies
    # spectrogram(f, t, zxx)

    # display the first few periods of the sin wave alongside its reconstruction
    # graph_sines(old_samples, new_samples)
    # you can see that the new wave (yellow) is oscillating slower than the original (blue)
    # this is because its frequency is now slightly lower


if __name__ == '__main__':
    main()
