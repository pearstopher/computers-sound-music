# CS410 Computers, Sound & Music
# Homework #4
# Christopher Juncker
#

import numpy as np
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


###############
# NOTE PITCHES
###############

# Each measure will start with the root note of the major scale, and then continue
# with randomly-selected notes of the major scale for the remaining beats. These
# randomly-selected tones should be chosen from scale notes 2..8.
def generate_notes():
    # create an array of the root's major scale
    major_scale = np.array([2, 4, 5, 7, 9, 11, 12])
    major_scale += args.root

    # create an array of random notes from the major scale
    note_array = np.array([np.random.choice(major_scale) for _ in range(args.beats)])

    # set the first element to the root
    note_array[0] = args.root

    # convert the midi notes to frequencies
    note_array = midi_to_freq(note_array)

    return note_array


###############
# NOTE VOLUMES
###############

# The formula you want for a given amplitude (0..1) given a volume knob setting  (0..10)
def vol_to_amp(volume):
    amplitude = 10 ** ((-6*(10 - volume)) / 20)
    return amplitude


root_amp = vol_to_amp(args.accent)
amp = vol_to_amp(args.volume)


################
# NOTE ENVELOPE
################

# Use FRAC (args.ramp) as a fraction of the beat time for the attack/release time of the note envelope.
def envelope(samples):
    size = len(samples)
    envelope_size = int((size / args.beats) * args.ramp)

    # create an envelope going from 0 to 1
    # (well, not actually 0, that would just waste the first sample)
    ramp_up = np.linspace(0.01, 1, num=envelope_size)

    # apply the ram to the beginning of the array
    samples[0:envelope_size] *= ramp_up

    # instead of creating a ramp down, just flip the array and use the same ramp again :D
    samples = np.flip(samples)
    samples[0:envelope_size] *= ramp_up

    # flip back and return the samples with the envelope applied
    samples = np.flip(samples)
    return samples


###############
# PROGRAM LOOP
###############

# Based on the Pseudocode the assignment instructions

# first, set up pyaudio stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=48000,
                output=True)

# "repeat until interrupted
while True:
    # generate the notes for this measure
    notes = generate_notes()
    print(notes)

    # "play root frequency for beat interval (square wave, accent volume, ramp)
    bps = args.bpm/60  # beats per second
    spb = samples_per_beat = int(48000 / bps)  # samples per beat
    note = np.asarray([square_wave(notes[0], t) for t in np.linspace(0, (1/bps), spb)], dtype=np.float32)
    note = root_amp * envelope(note)  # apply amplitude and envelope
    stream.write(note.tobytes())

    # "for remaining beats
    for i in range(1, len(notes)):
        # "play frequency k for beat interval (sine wave, volume, ramp)
        note = np.asarray([sine_wave(notes[i], t) for t in np.linspace(0, (1/bps), spb)], dtype=np.float32)
        note = amp * envelope(note)  # apply amplitude and envelope
        stream.write(note.tobytes())


# tear down pyaudio stream (unreachable)
# stream.stop_stream()
# stream.close()
# p.terminate()
