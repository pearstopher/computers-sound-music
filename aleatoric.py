# CS410 Computers, Sound & Music
# Homework #4
# Christopher Juncker
#

import numpy as np
import scipy.io.wavfile as wf
import pyaudio
import math
import argparse

# THE ASSIGNMENT
# You will build a generator that plays a sequence of notes, most of which are randomly
# selected from a major scale.
#
# NOTE PITCHES
# Your program will continuously play random measures of music. Each measure will start
# with the root note of the major scale, and then continue with randomly-selected notes
# of the major scale for the remaining beats. These randomly-selected tones should be
# chosen from scale notes 2..8.
#
# For example, if the user has selected a C[3] major scale (key 72) and four beats per
# measure, your notes for a measure might be
#
#   C[3] (key 72)
#   F[3] (key 77)
#   C[4] (key 84)
#   A[4] (key 81)
#
# BEAT TIME
# Beats will be played at a tempo (time per beat) selected by the user. Tempo is normally
# specified in “beats per minute” (BPM) which is a bit of an annoying unit. Divide 60 by
# BPM to get seconds per beat.
#
# MEASURE ACCENTS AND VOLUME
# The first beat of each measure will be accented in two ways.
#
# The first beat will be a square wave tone, the rest of the beats will be sine wave tones.
#
# The first beat may have a different volume than the remaining beats. The user can select
# the volume for the first beat and for the remaining beats.
#
# As we have discussed many times, the volume of a note is logarithmic in the amplitude of
# that note. For this assignment, the user will be able to set a volume in the range 0 to 10,
# where 10 is full volume and 0 is 60dB down from that volume. (This means that the volume at
# 0 is not quite 0, but quiet enough to hardly hear. See this great TI Blog Post
# (https://e2e.ti.com/blogs_/archives/b/thesignal/posts/logarithmic-potentiometers) for an
# interesting discussion on this topic.) The formula you want for a given amplitude  (0..1)
# given a volume knob setting  (0..10) is:
#
#   A = 10 * [ (-6*(10 - v)) / 20 ]
#
# For our example, with user volumes 5 and 8, the output will thus be
#
#   C[3] (key 72), square wave, A = 0.03162277660168379
#   F[3] (key 77), sine wave, A = 0.251188643150958
#   C[4] (key 84), sine wave, A = 0.251188643150958
#   A[4] (key 81), sine wave, A = 0.251188643150958
#
# NOTE ENVELOPE
# If you don’t use some kind of envelope, played notes will click at the start and end. Use a
# trapezoidal attack-release envelope: ramp the envelope up from 0.0 to 1.0 over the attack
# period at the start of the note, and ramp back down from 1.0 to 0.0 over the release period
# at the end of the note. Make the attack and release times the same. Graphically, it looks
# like this:
#    _______
#   /       \   (Trapezoidal AR Envelope)
#
# instead of this:
#    _______
#   |       |
#
# Apply this envelope to the note by multiplying sample-by-sample.
#
# PSEUDOCODE
# In the end, your program should look roughly like this:
#
#   repeat until interrupted
#       play root frequency for beat interval (square wave, accent volume, ramp)
#       for remaining beats
#           k ← random key from scale up 1 to 8 scale steps from root
#           play frequency k for beat interval (sine wave, volume, ramp)
#
# COMMAND
# Your program should be named aleatoric — for example, aleatoric.py if you are writing Python,
# or aleatoric.cpp if you are writing C++.
#
# Your program should accept any combination of five command-line arguments. The default value
# to use if the argument is not given is in square brackets. Default numbers without a decimal
# point indicate integer arguments; default numbers with a decimal point indicate floating-point
# arguments.
#
#   --root KEYNUMBER: Use MIDI key number KEYNUMBER as the root tone of the scale. [48]
#   --beats SIG: Use a “time signature” of SIG beats per measure. [8]
#   --bpm BPM: Use a beat frequency of BPM beats per minute. [90.0]
#   --ramp FRAC: Use FRAC as a fraction of the beat time for the attack and release time for the note envelope. [0.5]
#   --accent VOLUME: Use the given VOLUME from 0..10 as the note volume for the first beat of each measure. [5.0]
#   --volume VOLUME: Use the given VOLUME from 0..10 as the note volume for the unaccented beats of each measure. [8.0]
#
# Keep the program textually quiet: no output should be printed during operation.
#
#

###################
# Helper Functions
###################


# frequency formula: the frequency f for MIDI key number k
def midi_to_freq(k):
    f = 440 * 2**((k-69)/12)
    return f


# formula for the value y of a square wave with frequency f at time t
def square_wave(f, t):
    y = 4 * math.floor(f*t) - 2 * math.floor(2*f*t) + 1
    return y


# formula for the value y of a sine wave with frequency f at time t:
def sine_wave(f, t):
    y = math.sin(2*math.pi*f*t)
    return y


###########
# COMMANDS
###########

parser = argparse.ArgumentParser()

# --root KEYNUMBER: Use MIDI key number KEYNUMBER as the root tone of the scale. [48]
parser.add_argument("--root", metavar="KEYNUMBER", type=int, default=48,
                    help="Use MIDI key number KEYNUMBER as the root tone of the scale. [48]")

# --beats SIG: Use a “time signature” of SIG beats per measure. [8]
parser.add_argument("--beats", metavar="SIG", type=int, default=8,
                    help="Use a “time signature” of SIG beats per measure.")

# --bpm BPM: Use a beat frequency of BPM beats per minute. [90.0]
parser.add_argument("--bpm", metavar="BPM", type=float, default=90.0,
                    help="Use a beat frequency of BPM beats per minute.")

# --ramp FRAC: Use FRAC as a fraction of the beat time for the attack/release time of the note envelope. [0.5]
parser.add_argument("--ramp", metavar="FRAC", type=float, default=0.5,
                    help="Use FRAC as a fraction of the beat time for the attack/release time of the note envelope.")

# --accent VOLUME: Use the given VOLUME from 0..10 as the note volume for the first beat of each measure. [5.0]
parser.add_argument("--accent", metavar="VOLUME", type=float, default=5.0,
                    help="Use the given VOLUME (0..10) as the note volume for the first beat of each measure.")

# --volume VOLUME: Use the given VOLUME from 0..10 as the note volume for the unaccented beats of each measure. [8.0]
parser.add_argument("--volume", metavar="VOLUME", type=int, default=8.0,
                    help="Use the given VOLUME (0..10) as the note volume for the unaccented beats of each measure.")

args = parser.parse_args()






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
