# Homework 4

Christopher Juncker

*Prompt: Briefly describe what you did, how it went, and what is still to be done.*

## To do

(This is just the leftover readme from the old assignment 3)

## Setup

In order to set up this project, I started out with my code from Homework #1. I
modified the base class so that instead of holding a single frequency, it instead
held a string signifying the type of chord to make, as described in the assignment
handout:

```python
example_1 = "Ebm equal"  # E flat minor, equal temperament
example_2 = "C just"  # C major, just temperament
```

## Input

In order to process the input to my program, I set up two functions. The first
is called by my program which then prompts the user to enter a chord:

```python
cs = ChordSamler()
cs.input()  # prompt the user to input the type of chord
```

There is a second function which can also be used to set a chord directly,
without asking the user for input:

```python
cs.set("C just")  # set a specific chord without user input
```

After calling either function, the input string is processed and the correct
frequencies are generated to correspond to the requested chord.

## Output

Just as with my Homework #1, the user can either `play()` their sound or 
`write()` their sound to disk. When writing to disk, the sound file which is
created is automatically given a name corresponding to the string which was 
used to generate the chord. This file meets all the specifications listed in 
the assignment.


