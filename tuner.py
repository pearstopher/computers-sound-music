# CS410 Computers, Sound & Music
# Homework #3 Tuner
# Christopher Juncker

import sys
import pyaudio
import numpy as np
import scipy.fft
import scipy.io.wavfile as wf


# "Build an instrument tuner with two modes:
#
# MODE 1
# "report the frequency of a 48Ksps WAV file
if len(sys.argv) == 2:

    # read in the file
    sample_rate, samples = wf.read(sys.argv[1])

    # "To report the frequency of a WAV file:
    # "1. Trim the file to the first 2^17 samples (a few seconds) if it is longer than that.
    # "   If it is shorter, trim to the largest possible power of 2.
    power = 0
    while 2 ** (power + 1) <= len(samples) and power < 17:
        power += 1
    WINDOW = 2 ** power
    samples = samples[:WINDOW]

    # "2. Apply a triangular window to the samples.
    # "   You can construct this window (linear increase from 0 to 1 halfway,
    # "   then linear decrease to 0 at the end) manually, or get it from somewhere.
    #
    # I'm going to use a Bartlett window because it's totally a triangle
    window = np.bartlett(len(samples))
    samples = np.multiply(window, samples)

    # "3. Take the DFT of the windowed samples.
    f = scipy.fft.rfft(samples)

    # "4. Find the largest bin in the DFT.
    # "You can use the abs() function in Python to get the magnitude of a complex number.
    largest = np.argmax(abs(f))

    # "5. Report the center frequency of that bin.
    print(largest * (sample_rate / WINDOW))


# MODE 2
# "continuously report the frequency of a 48Ksps live input.
if len(sys.argv) == 1:

    # "To continuously report the frequency of a live input,
    # "start taking samples from the live input.
    # "For every 8192 samples, do steps 2-5
    BUFFER = 8192
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    # "48Ksps WAV file... 48Ksps live input
    RATE = 48000
    SECONDS = 60*5  # let's stop after 5 minutes

    p = pyaudio.PyAudio()
    iStream = p.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=BUFFER)

    for _ in range(0, int((RATE * SECONDS) / BUFFER)):
        # get the data from the stream
        data = iStream.read(BUFFER)
        data = np.frombuffer(data, dtype=np.int16)

        # "2. Apply a triangular window to the samples.
        # "   You can construct this window (linear increase from 0 to 1 halfway,
        # "   then linear decrease to 0 at the end) manually, or get it from somewhere.
        #
        # I'm going to use a bartlett window because it's totally a triangle
        window = np.bartlett(len(data))
        data = np.multiply(window, data)

        # "3. Take the DFT of the windowed samples.
        f = scipy.fft.rfft(data)

        # "4. Find the largest bin in the DFT.
        # "You can use the abs() function in Python to get the magnitude of a complex number.
        largest = np.argmax(abs(f))

        # "5. Report the center frequency of that bin.
        print(largest * (RATE / BUFFER))

    iStream.stop_stream()
    iStream.close()
    p.terminate()
