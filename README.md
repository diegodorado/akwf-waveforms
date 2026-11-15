# AKWF Wavetables

AKWF waveforms by [Adventure Kid](https://www.adventurekid.se/akrt/waveforms/adventure-kid-waveforms/), resampled to 2048 samples per cycle and concatenated into WAV files for use as wavetables in [Strudel](https://strudel.cc/).

The `build.py` script documents how the original AKWF samples are sourced, resampled, and organized into wavetable banks.

## Usage

```javascript
samples('github:diegodorado/akwf-waveforms')
```

```javascript
n(run(8)).scale("d:ritusen")
.s("wt_epiano")
.wtrate(.01)
.lpf(2000).lpe(3)
.delay(.5).dfb(.3).room(.3).size(3)
```

```javascript
n("[0,2,4,6,8]").scale("g:minor")
.s("wt_flute")
.wt(.3).wtrate(.25).wtdepth(.3)
.att(.1).rel(.3).clip(.8)
.spread(.2).detune(.2).unison(8)
.delay(.3).dfb(.3).room(.6).size(4)
```
