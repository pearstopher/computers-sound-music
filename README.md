# Homework 4

Christopher Juncker

*Prompt: Briefly describe what you did, how it went, and what is still to be done.*



## Setup

I hadn't used `argparse` in Python yet so the first step of this program was reading
their documentation and learning how to set up the arguments. This program can be
run with any of five arguments which are described fully in the assignment handout and
in the comments at the start of `aleatoricpy`. Essentially, the program can be run as
follows:

```bash
# default settings, assignment example #1
> python aleatoric.py

# custom settings, assignment example #2
> python aleatoric.py --ramp 0.05 --bpm 240 --root 84 --accent 5 --volume 5
```

## Conversions

After the arguments were set up, the next step was to create some basic functions to
perform the conversions that I would need in order to correctly run the program. I
created the following "helper functions" which I knew I would be using later:

```python
# frequency formula: the frequency f for MIDI key number k
def midi_to_freq(k): ...

# formula for the value y of a square wave with frequency f at time t
def square_wave(f, t): ...

# formula for the value y of a sine wave with frequency f at time t:
def sine_wave(f, t): ...

# The formula you want for a given amplitude (0..1) given a volume knob setting  (0..10)
def vol_to_amp(volume): ...
```

## Envelopes

Next I created the code to apply the envelopes to the samples. I created a "ramp up"
filter to apply to the beginning of the samples. Then, thinking myself rather clever,
I decided not to create a second "ramp down" filter to apply to the end of the array.
Instead, I simply reversed the array and applied the first filter to the start of the
backwards samples before flipping them forwards again. I know `numpy` doesn't actually
flip the array itself, just the view of the array, so this should be efficient enough.

## Note Generation

I created a quick little function which generated a measure full of note frequencies
based on the program arguments. The notes are all part of the major scale and the
first note is always the root note, just like the assignment specifies. As expected,
the functions that I had created earlier were helpful here.

## Main Loop

Now that I had built all the pieces, all that was left to do was to create a loop
and output the samples. I used Pyaudio to create an audio stream, and then followed
the pseudocode given in the assignment to generate each loop of audio. The first
note in each measure (the root) was generated as a square wave. The subsequent notes
were generated as sine waves. I applied the envelope filter and the correct amplitude
to each note before adding the note to the output stream.

## Conclusion

I had a lot of fun working on this assignment. I have confirmed that the sound of my
program matches the sound of the two example WAV files provided along with the
assignment. There are still some areas where I could increase the efficiency of the
program, like using `numpy` functions to help generate the sine and square wave arrays
quickly instead of looping and generating them sample by sample. But I am content for
now with my progress and believe that I have successfully met each of the program
requirements!
