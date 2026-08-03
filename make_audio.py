#!/usr/bin/env python3
"""Render the hymn to audio with sampled instruments (choir + pipe organ).

Builds the performance directly from the note tables in gen_musicxml.py,
renders it through a General MIDI soundfont, and applies a convolution
hall reverb.

Requires:  pip install tinysoundfont mido numpy   (plus ffmpeg for the MP3)
Soundfont: GeneralUser GS, downloaded automatically if not present.
Usage:     python3 make_audio.py [path/to/soundfont.sf2]
"""
import os
import subprocess
import sys
import wave

import numpy as np
import tinysoundfont

import gen_musicxml as score   # note tables S/A/T/B + pitch parser

SF2 = sys.argv[1] if len(sys.argv) > 1 else 'GeneralUserGS.sf2'
SF2_URL = 'https://github.com/mrbumpy409/GeneralUser-GS/raw/main/GeneralUser-GS.sf2'
WAV = 'Cantique.wav'
MP3 = 'Cantique.mp3'

SR = 44100
BPM = 104                      # sturdy hymn tempo
DIV = 2                        # table divisions per quarter note
TOTAL_DIVS = 2 + 8 * 15 + 6    # pickup + 15 full measures + final dotted half

SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi_pitch(p):
    step, alter, octave, _ = score.parse(p)
    return 12 * (octave + 1) + SEMITONE[step] + alter


# --- tempo map: steady, easing ~30% over the last full measure, final chord held
def build_time_map():
    base = 60.0 / BPM / DIV
    rit_start, rit_end = TOTAL_DIVS - 14, TOTAL_DIVS - 6   # measure 16
    cum, t = [0.0], 0.0
    for d in range(TOTAL_DIVS):
        f = 1.0
        if d >= rit_end:
            f = 1.45                                        # held final chord
        elif d >= rit_start:
            f = 1.0 + 0.30 * (d - rit_start) / (rit_end - rit_start)
        t += base * f
        cum.append(t)
    return cum


def voice_events(table):
    """[(start_div, dur_div, midi, measure_beat0)] for one voice."""
    evs, t = [], 0
    for mn in range(1, 18):
        for p, d in table[mn]:
            evs.append((t, d, midi_pitch(p), t % 8 == 2))   # downbeats: div 2, 10, ...
            t += d
    return evs


def main():
    if not os.path.exists(SF2):
        print(f'downloading soundfont to {SF2} ...')
        subprocess.run(['curl', '-sL', '-o', SF2, SF2_URL], check=True)

    cum = build_time_map()
    rng = np.random.default_rng(7)

    # (table, choir velocity): soprano leads, bass firm, inner voices blended
    voices = [(score.S, 92), (score.A, 78), (score.T, 78), (score.B, 86)]

    CHOIR, ORGAN = 52, 19       # GM: Choir Aahs, Church Organ
    GAP = 0.035                 # re-articulation gap between notes (seconds)

    events = []                 # (time, 'on'/'off', channel, key, velocity)
    for vi, (table, vel) in enumerate(voices):
        for start, dur, key, downbeat in voice_events(table):
            t0 = cum[start] + float(rng.uniform(0.0, 0.010))
            t1 = cum[start + dur] - (0.0 if start + dur == TOTAL_DIVS else GAP)
            v = min(112, vel + (6 if downbeat else 0) + int(rng.integers(-4, 5)))
            events.append((t0, 'on', vi, key, v))            # choir
            events.append((t1, 'off', vi, key, 0))
            events.append((t0, 'on', vi + 4, key, int(v * 0.55)))   # organ 8'
            events.append((t1, 'off', vi + 4, key, 0))
            if vi == 3:                                      # organ 16' pedal
                events.append((t0, 'on', 8, key - 12, int(v * 0.40)))
                events.append((t1, 'off', 8, key - 12, 0))
    events.sort(key=lambda e: e[0])

    synth = tinysoundfont.Synth(gain=-3.0)
    sfid = synth.sfload(SF2)
    for ch in range(4):
        synth.program_select(ch, sfid, 0, CHOIR)
        synth.program_select(ch + 4, sfid, 0, ORGAN)
    synth.program_select(8, sfid, 0, ORGAN)

    tail = 3.0                  # reverb tail after the release
    total = events[-1][0] + tail
    chunks, now = [], 0.0
    for t, kind, ch, key, v in events + [(total, 'end', 0, 0, 0)]:
        n = int(round((t - now) * SR))
        if n > 0:
            chunks.append(np.frombuffer(synth.generate(n), dtype=np.float32))
            now = t
        if kind == 'on':
            synth.noteon(ch, key, v)
        elif kind == 'off':
            synth.noteoff(ch, key)
    dry = np.concatenate(chunks).reshape(-1, 2).astype(np.float64)

    # --- convolution hall reverb: 2.4 s decorrelated exponential decay,
    # darkened highs, 18 ms predelay, ~26% wet
    n_ir = int(2.4 * SR)
    t_ir = np.arange(n_ir) / SR
    ir = rng.standard_normal((n_ir, 2)) * np.exp(-t_ir / 0.85)[:, None]
    spec = np.fft.rfft(ir, axis=0)
    freqs = np.fft.rfftfreq(n_ir, 1 / SR)
    ir = np.fft.irfft(spec / (1.0 + (freqs / 3500.0) ** 2)[:, None], n=n_ir, axis=0)
    ir = np.vstack([np.zeros((int(0.018 * SR), 2)), ir])
    ir /= np.sqrt((ir ** 2).sum(axis=0)).max()

    n_fft = 1 << int(np.ceil(np.log2(len(dry) + len(ir) - 1)))
    wet = np.fft.irfft(np.fft.rfft(dry, n_fft, axis=0) *
                       np.fft.rfft(ir, n_fft, axis=0), n_fft, axis=0)[:len(dry)]
    mix = dry + 0.26 * wet
    mix *= 0.89 / np.abs(mix).max()

    with wave.open(WAV, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())
    print(f'wrote {WAV} ({len(mix)/SR:.1f}s)')

    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', WAV,
                    '-codec:a', 'libmp3lame', '-q:a', '2', MP3], check=True)
    print(f'wrote {MP3}')


if __name__ == '__main__':
    main()
