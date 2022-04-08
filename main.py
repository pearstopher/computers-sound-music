# CS410 Computers, Sound & Music
#
# Plays a short version of the song "Frequency"
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


def main():
    # play the song
    s = Samples()
    s.play()

    # apply Short Time Fourier Transform (STFT) to samples
    f, t, zxx = signal.stft(s.master, fs=s.sample_rate, nperseg=s.sample_rate/2)

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
    _, new_samples = signal.istft(zxx, s.sample_rate)
    s.master = np.copy(new_samples)

    # play the reconstructed sin wave
    s.play()


if __name__ == '__main__':
    main()
