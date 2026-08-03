#!/usr/bin/env python3
"""Sing the hymn with ISiS (IRCAM Singing Synthesis) and mix SATB.

Voices: EL (lyric soprano) on soprano, MS (mezzo) on alto, RT (tenor)
on tenor and bass. Scores come from gen_isis_scores.py.

Requires the ISiS distribution + voices unpacked under ./ISiS/ (IRCAM
Forum account needed to download; not redistributed in this repo).
Usage: python3 gen_isis_scores.py && python3 make_isis_audio.py
"""
import os
import subprocess
import wave

import numpy as np

ISIS = 'ISiS/ISiS_V1.3.0_Linux_x86_64/isis.sh'
CORPORA = os.path.abspath('ISiS')
MP3 = 'Cantique_sung_isis.mp3'
SR = 48000                      # ISiS native rate

# (part, ISiS voice, gain, pan)
VOICES = [
    ('S', 'EL', 0.95, -0.25),
    ('A', 'MS', 0.90, 0.25),
    ('T', 'RT', 0.90, -0.25),
    ('B', 'RT', 1.00, 0.25),
]


def render(part, voice):
    out = f'isis_{part}.wav'
    env = dict(os.environ, ISIS_CORPORA=CORPORA)
    subprocess.run([ISIS, '-m', f'Cantique_{part}.isis.cfg', '-sv', voice,
                    '--seed', '17', '-o', out],
                   check=True, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


def load(fn):
    with wave.open(fn) as w:
        assert w.getframerate() == SR, (fn, w.getframerate())
        x = np.frombuffer(w.readframes(w.getnframes()),
                          dtype='<i2').astype(np.float64) / 32767
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(axis=1)
    return x


def main():
    tracks = []
    for part, voice, gain, pan in VOICES:
        print(f'--- ISiS: rendering {part} with {voice}')
        x = load(render(part, voice))
        tracks.append((x, gain, pan))

    n = max(len(x) for x, _, _ in tracks) + SR
    mix = np.zeros((n, 2))
    for x, gain, pan in tracks:
        st = np.stack([x * (1 - pan) / 2 + x / 2,
                       x * (1 + pan) / 2 + x / 2], 1)
        mix[:len(x)] += gain * st

    # hall reverb (same design as the other renders)
    rng = np.random.default_rng(7)
    n_ir = int(2.2 * SR)
    t_ir = np.arange(n_ir) / SR
    ir = rng.standard_normal((n_ir, 2)) * np.exp(-t_ir / 0.8)[:, None]
    freqs = np.fft.rfftfreq(n_ir, 1 / SR)
    ir = np.fft.irfft(np.fft.rfft(ir, axis=0) /
                      (1.0 + (freqs / 3200.0) ** 2)[:, None], n=n_ir, axis=0)
    ir = np.vstack([np.zeros((int(0.02 * SR), 2)), ir])
    ir /= np.sqrt((ir ** 2).sum(axis=0)).max()
    n_fft = 1 << int(np.ceil(np.log2(len(mix) + len(ir))))
    wet = np.fft.irfft(np.fft.rfft(mix, n_fft, axis=0) *
                       np.fft.rfft(ir, n_fft, axis=0), n_fft, axis=0)[:len(mix)]
    mix = mix + 0.30 * wet
    mix *= 0.89 / np.abs(mix).max()

    with wave.open('Cantique_sung_isis.wav', 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                    '-i', 'Cantique_sung_isis.wav',
                    '-codec:a', 'libmp3lame', '-q:a', '2', MP3], check=True)
    print('wrote', MP3)


if __name__ == '__main__':
    main()
