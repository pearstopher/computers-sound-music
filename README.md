# Homework 2

Christopher Juncker

*Prompt: Briefly describe what you did, how it went, and what is still to be done.*


## Setup

Since HW1 involved creating WAV files from scratch, I started this assignment by
writing some new code which was capable of reading pre-recorded WAV files from
disk. Once my code was able to successfully read and write pre-existing audio
files, I was ready to start the real assignment: building the filter and
adjusting the bit rate.

## Filtering

For practice, I began by creating the "Simple FIR Lowpass Filter" as described 
in the `Digital Audio Filters -> FIR Filters` course page:

```python
y[i] = (x[i] + x[i-1]) / 2
```

After confirming that my simple filter worked, I went ahead and implemented a
'higher order filter' as explained the same course page and later described as:

```python
y[i] = Σ(j=0, N-1) a[j]x[i-j]
```

I used the same filter coefficients as the ones provided in the course github
at https://github.com/pdx-cs-sound/hw-resample. I followed the instructions in
the provided code in order to generate these coefficients dynamically at 
resampling time.

My second filter takes a long time to process the audio since it is has to loop
through all the coefficients for every index in the new sample. Although it was
fun to write everything by hand myself for the assignment, in the future I would 
definitely use more efficient methods. The exact same convolution that I am doing
with loops can also be accomplished using `np.convolve` and `scipy.signal.convolve`
in a tiny fraction of the amount of time it takes my program to resample using my
own slow algorithm. It takes my PC almost 3 minutes to resample all three of the
files for the assignment. The library functions accomplish the same task almost
instantaneously. (I have left a few lines of commented-out code at the bottom of
my filter function which describe how to run the filter using the faster library
functions.)


## Testing

I tested my program by generating lots of copies of the audio files provided in
the assignment as I worked on the filter. Then I used three methods to confirm 
that my files had been resampled successfully:

1. I listened to each copy to confirm that the half-rate file sounded the same as 
the original (I couldn't really tell a difference even with the "simple" filter 
to be completely honest). 

2. I inspected each new file in Audacity to see how the waveforms looked and to 
confirm that everything was working as intended. This was helpful in determining
that my original filter was originally shifting all the new samples by a small
amount due to me not having the filter window centered over the correct sample.

3. I used each file to generate a spectrogram using the SoX utility and confirmed
that all the high frequencies in the original file were successfully removed from
the resampled file, and that all the low frequencies in the resampled file appeared
to be unchanged.