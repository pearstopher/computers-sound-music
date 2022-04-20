# Homework 3

Christopher Juncker

*Prompt: Briefly describe what you did, how it went, and what is still to be done. 
Please include detailed build instructions.*


## Instructions


### Install
```shell
python -m pip install numpy scipy pyaudio
```
### Run
```shell
# run with live audio input
python tuner.py

# run with file input
python tuner.py file.wav
```

## Phase 1: Live Audio

Ever since the first assignment in this class, I really wanted to learn how to capture
live audio input. Of course, I never got around to actually figuring it out, so I am
really glad that it was part of this assignment. The first phase of this assignment was
simply learning how to read in live audio from my webcam microphone. To my surprise, it
was really not difficult at all. I made a little program that recorded my voice for a
few seconds and then played it back to me.

## Phase 2: Bartlett Window

Once I was confident in my ability to work with a live audio stream, the second phase
was to figure out a good function to window the data. I chose a Bartlett window, which
is a great triangular window and which can be easily generated using `numpy.Bartlett`.

## Part 3: Discrete Fourier Transform

I wasn't too worried about this part since I already have practiced a little bit with
using a few different versions of the Fourier Transform which are included in the
`scipy.signal` library. Applying the DFT to the window of samples and finding the
largest frequency was pretty straightforward.

## Part 4: Testing

Everything appears to be working great. I tested the WAV file functionality of the
program by reading in two `sine.wav` files from the class, one with a 440Hz sine wave
and one with a 1000Hz sine wave. My program correctly identified both of these 
frequencies.

I tested the live audio functionality of the program by playing my guitar in front of
my computer to see if it would output the correct frequency for the notes that I was
playing. Although this didn't work perfectly, it still worked surprisingly well. When
I played the low E string on my guitar, my tuner alternated back and forth between
reporting 165Hz and 330Hz. Since the E string corresponds to 82.4Hz, these values 
clearly represent the second and third overtones of the correct fundamental frequency.
When playing an A on my guitar, my tuner was in fact able to display the correct
frequency of 110Hz about half of the time (it would display 220Hz otherwise).
