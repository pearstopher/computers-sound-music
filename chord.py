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
                 amplitude=0.167,
                 duration=1.0,
                 sample_rate=48000,
                 chord="Am",
                 temperament="just",
                 ):
        self.channels = channels
        self.bits = bits
        self.amplitude = amplitude
        self.duration = duration
        self.sample_rate = sample_rate
        self.chord = chord
        self.temperament = temperament
        self.notes, self.freqs = self.process_c_t()

    # get chord and temperament from user input
    def input(self):
        c_t = input("Please Enter a chord and temperament (ex1. 'A equal', ex2. 'Ebm just'): ")
        self.chord, self.temperament = c_t.split()
        self.notes, self.freqs = self.process_c_t()

    # get chord and temperament from argument
    def set(self, c_t):
        self.chord, self.temperament = c_t.split()
        self.notes, self.freqs = self.process_c_t()

    # process chord and temperament
    def process_c_t(self):

        # name_to_key and just_ratios from:
        # https://github.com/pdx-cs-sound/hw-chord/blob/master/tables.py
        # Conversion table: Note names to MIDI key numbers.
        name_to_key = {
            "C": 72,
            "Db": 73,
            "D": 74,
            "Eb": 75,
            "E": 76,
            "F": 77,
            "Gb": 78,
            "G": 79,
            "Ab": 80,
            "A": 81,
            "Bb": 82,
            "B": 83,
        }
        just_ratios = [
            1,
            16/15,
            9/8,
            6/5,
            5/4,
            4/3,
            45/32,
            3/2,
            8/5,
            5/3,
            9/5,
            15/8,
        ]

        # https://gist.github.com/YuxiUx/ef84328d95b10d0fcbf537de77b936cd
        def midi_to_frequency(note):
            a = 440
            return (a / 32) * (2 ** ((note - 9) / 12))

        notes = []
        freqs = []

        # get frequency of first note
        if len(self.chord) == 1 or (len(self.chord) == 2 and self.chord[1] == "m"):
            notes.append(name_to_key[self.chord[0]])
            freqs.append(midi_to_frequency(notes[0]))
        else:
            notes.append(name_to_key[self.chord[0] + self.chord[1]])
            freqs.append(midi_to_frequency(notes[0]))

        # get frequency of second note
        if (len(self.chord) == 2 and self.chord[1] == "m") or \
                (len(self.chord) == 3 and self.chord[2] == "m"):
            if self.temperament == "equal":
                notes.append(notes[0] + 3)
                freqs.append(midi_to_frequency(notes[1]))
            else:
                freqs.append(freqs[0] * just_ratios[3])
        else:
            if self.temperament == "equal":
                notes.append(notes[0] + 4)
                freqs.append(midi_to_frequency(notes[1]))
            else:
                freqs.append(freqs[0] * just_ratios[4])

        # get frequency of third note
        if self.temperament == "equal":
            notes.append(notes[0] + 7)
            freqs.append(midi_to_frequency(notes[2]))
        else:
            freqs.append(freqs[0] * just_ratios[7])

        return notes, freqs


# class which creates samples based on Spec
class ChordSampler(Spec):
    # def __init__(self, channels=None, bits=None, amplitude=None, duration=None,
    #             sample_rate=None, chord=None, temperament=None):
    #    super().__init__(channels, bits, amplitude, duration, sample_rate, chord, temperament)
    def __init__(self):
        super().__init__()
        # set max value for current number of bits
        self.max = 2**(self.bits - 1) - 1
        self.min = -self.max - 1
        # generate the samples
        self.samples = None
        self.generate_samples()

    def generate_samples(self):
        s1 = ((self.amplitude * self.max) *
              np.sin((2*np.pi) *
              (np.arange(self.sample_rate*self.duration)) *
              (self.freqs[0]/self.sample_rate)))
        s2 = ((self.amplitude * self.max) *
              np.sin((2*np.pi) *
              (np.arange(self.sample_rate*self.duration)) *
              (self.freqs[1]/self.sample_rate)))
        s3 = ((self.amplitude * self.max) *
              np.sin((2*np.pi) *
              (np.arange(self.sample_rate*self.duration)) *
              (self.freqs[2]/self.sample_rate)))

        self.samples = s1 + s2 + s3

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
    def write(self):
        file = self.chord + "-" + self.temperament + ".wav"
        samples = self.samples.astype(np.int16)
        wf.write(file, self.sample_rate, samples)


def main():
    print("Homework 3")

    s = ChordSampler()

    s.input()
    s.generate_samples()
    s.write()

    # play a song with some nice chords :)
    # for i in range(5):
    #     s.set("C", "equal")
    #     s.generate_samples()
    #     s.play()
    #
    #     s.set("F", "equal")
    #     s.generate_samples()
    #     s.play()
    #
    #     s.set("Am", "equal")
    #     s.generate_samples()
    #     s.play()
    #
    #     s.set("G", "equal")
    #     s.generate_samples()
    #     s.play()


if __name__ == '__main__':
    main()
