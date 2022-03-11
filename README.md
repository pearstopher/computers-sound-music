# Homework 2

Christopher Juncker

*Prompt: Briefly describe what you did, how it went, and what is still to be done.*


## Setup

Since HW1 involved creating WAV files from scratch, I started this assignment by
writing some new code which was capable of reading pre-recorded WAV files from
disk. Once my code was able to successfully read, play, and write pre-existing
audio files, I was ready to start the real assignment: building the filter and
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
at https://github.com/pdx-cs-sound/hw-resample. I follow the instructions in
the provided code in order to generate these coefficients at resampling time.



## Testing

...