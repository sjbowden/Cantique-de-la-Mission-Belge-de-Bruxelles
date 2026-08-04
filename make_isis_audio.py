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

import glob
_isis_hits = sorted(glob.glob('ISiS/ISiS_V*/isis.sh'))
assert _isis_hits, 'ISiS not found under ./ISiS/ — see README "Getting ISiS"'
ISIS = _isis_hits[-1]
CORPORA = os.path.abspath('ISiS')
SR = 48000                      # ISiS native rate

# (part, ISiS voice, gain, pan)
VOICES = [
    ('S', 'EL', 0.95, -0.25),
    ('A', 'MS', 0.90, 0.25),
    ('T', 'RT', 0.90, -0.25),
    ('B', 'RT', 1.00, 0.25),
]

# The bass is RT (a tenor) transposed below his range; also offer a mix
# without it. (name, parts included)
MIXES = [
    ('Cantique_sung', 'SATB'),
    ('Cantique_sung_no_bass', 'SAT'),
]


def render(part, voice):
    out = f'isis_{part}.wav'
    env = dict(os.environ, ISIS_CORPORA=CORPORA)
    # 'make isis-mkl-fix' installs this shim for non-Intel CPUs, where the
    # bundled MKL would otherwise demand a kernel that isn't shipped
    shim = os.path.join(os.path.dirname(ISIS), 'ISiS', '_internal',
                        'libfakeintel.so')
    if os.path.exists(shim):
        env['LD_PRELOAD'] = shim + ':' + env.get('LD_PRELOAD', '')
    r = subprocess.run([ISIS, '-m', f'Cantique_{part}.isis.cfg', '-sv', voice,
                        '--seed', '17', '-o', out],
                       env=env, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        tail = '\n'.join(r.stdout.splitlines()[-25:])
        raise RuntimeError(
            f'ISiS failed for part {part} (voice {voice}), exit '
            f'{r.returncode}. Last output:\n{tail}')
    return out


def load(fn):
    with wave.open(fn) as w:
        assert w.getframerate() == SR, (fn, w.getframerate())
        x = np.frombuffer(w.readframes(w.getnframes()),
                          dtype='<i2').astype(np.float64) / 32767
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(axis=1)
    return x


def reverb(mix):
    """hall reverb (same design as the other renders)"""
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
    return mix * (0.89 / np.abs(mix).max())


def main():
    missing = sorted({v for _, v, _, _ in VOICES
                      if not os.path.isdir(os.path.join(CORPORA, v))})
    if missing:
        raise SystemExit(
            f'ISiS voice database(s) not found under {CORPORA}: '
            f'{", ".join(missing)}. Unpack the voice archives there '
            '(see README "Getting ISiS").')
    tracks = {}
    for part, voice, gain, pan in VOICES:
        print(f'--- ISiS: rendering {part} with {voice}')
        x = load(render(part, voice))
        tracks[part] = (x, gain, pan)

    for name, parts in MIXES:
        n = max(len(tracks[p][0]) for p in parts) + SR
        mix = np.zeros((n, 2))
        for p in parts:
            x, gain, pan = tracks[p]
            st = np.stack([x * (1 - pan) / 2 + x / 2,
                           x * (1 + pan) / 2 + x / 2], 1)
            mix[:len(x)] += gain * st
        mix = reverb(mix)
        with wave.open(f'{name}.wav', 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((mix * 32767).astype('<i2').tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                        '-i', f'{name}.wav',
                        '-codec:a', 'libmp3lame', '-q:a', '2',
                        f'{name}.mp3'], check=True)
        print('wrote', f'{name}.mp3')


if __name__ == '__main__':
    main()
