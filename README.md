# Homework 1

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
python main.py
```

## Part 1

For Part 1 of this assignment, I created a very simple class to hold the specification
information provided in the assignment. Then I built a second class from this which used
the specification information to generate an array of samples. After generating the 
samples, I used the `wavefile` functionality included in the `scipy` library to write 
my array to a file named `sine.wav`.

## Part 2

For Part 2, I implemented a few additional lines of code which clipped the samples in
the array. Then I simply called my function from Part 1 a second time in order to write 
the new samples to another audio file `clipped.wav` as instructed.

## Part 3

For Part 3, I used the `pyaudio` library to play both of the files which are generated
by my program on my computer's speakers. I had a little trouble getting `pyaudio`
installed on my computer, but once that was out of the way everything was pretty
straight-forward.

## Conclusion

I believe that I have successfully completed all the parts of this assignment. I had
a lot of fun, and I would say that everything went great!

