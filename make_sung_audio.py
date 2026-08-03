#!/usr/bin/env python3
"""Sing the hymn (free/open-source route): eCantorix + espeak + MBROLA.

Renders each voice's karaoke MIDI (from gen_sung_midi.py) through
eCantorix singing synthesis with French voices, then mixes the four
parts with a hall reverb into Cantique_sung_demo.mp3.

System packages:
    sudo apt-get install -y espeak sox libmidi-perl libconfig-tiny-perl \
        libmath-fft-perl mbrola mbrola-fr1 mbrola-fr4
Python: pip install numpy mido   (ffmpeg for the MP3)
Usage:  python3 gen_sung_midi.py && python3 make_sung_audio.py
"""
import os
import shutil
import subprocess
import wave

import numpy as np

ECANTORIX = 'ecantorix'
ECANTORIX_URL = 'https://github.com/divVerent/ecantorix.git'
SR = 44100
MP3 = 'Cantique_sung_demo.mp3'

# (part, mbrola voice, espeak fallback, mix gain, pan L..R)
VOICES = [
    ('S', 'mb-fr4', 'fr+f2', 1.00, -0.25),
    ('A', 'mb-fr4', 'fr+f4', 0.85, 0.25),
    ('T', 'mb-fr1', 'fr+m3', 0.85, -0.25),
    ('B', 'mb-fr1', 'fr+m1', 0.95, 0.25),
]

# mb-fr1's pitch response to espeak's -p is not monotonic, which breaks
# eCantorix's binary-search calibration ("CACHE INCONSISTENCY"). Disabling
# the pitch cache makes it measure and correct every sample individually.
NOCACHE_CTRL = 'ecantorix_nocache.pl'
NOCACHE_VOICES = {'mb-fr1'}


def have_mbrola(voice):
    if not shutil.which('mbrola'):
        return False
    lang = voice.split('-')[1]
    return any(os.path.exists(p) for p in (
        f'/usr/share/mbrola/{lang}/{lang}',
        f'/usr/share/mbrola/voices/{lang}',
        f'/usr/share/mbrola/{lang}'))


def render_voice(part, voice):
    out = f'sung_{part}.wav'
    cache = f'.ecantorix-cache-{voice.replace("+", "_")}'
    os.makedirs(cache, exist_ok=True)
    env = dict(os.environ)
    # Math::FFT isn't packaged for Ubuntu; a local CPAN build lives in ./perl5
    # (perl Makefile.PL INSTALL_BASE=$PWD/perl5 && make install)
    local_perl = os.path.abspath('perl5/lib/perl5')
    if os.path.isdir(local_perl):
        env['PERL5LIB'] = local_perl + ':' + env.get('PERL5LIB', '')
    extra = []
    if voice in NOCACHE_VOICES:
        with open(NOCACHE_CTRL, 'w') as f:
            f.write('our $ESPEAK_PITCH_CACHE = 0;\nour $ESPEAK_ATTEMPTS = 3;\n1;\n')
        extra = ['-C', os.path.abspath(NOCACHE_CTRL)]   # 'do' needs a full path
    subprocess.run(
        ['perl', os.path.join(ECANTORIX, 'ecantorix.pl'),
         '-v', voice, '-r', str(SR), '-c', cache,
         '-t', '24'] + extra +      # cancel eCantorix's default -24 transpose
        ['-O', 'wav', '-o', out, f'Cantique_{part}.mid'],
        check=True, env=env)
    return out


def load_wav(fn):
    with wave.open(fn) as w:
        assert w.getframerate() == SR, (fn, w.getframerate())
        x = np.frombuffer(w.readframes(w.getnframes()),
                          dtype='<i2').astype(np.float64) / 32767
        if w.getnchannels() == 2:
            x = x.reshape(-1, 2).mean(axis=1)
    return x


def main():
    if not os.path.exists(ECANTORIX):
        subprocess.run(['git', 'clone', '--depth', '1', ECANTORIX_URL,
                        ECANTORIX], check=True)

    tracks = []
    for part, mb, fallback, gain, pan in VOICES:
        voice = mb if have_mbrola(mb) else fallback
        print(f'--- rendering {part} with voice {voice}')
        x = load_wav(render_voice(part, voice))
        tracks.append((x, gain, pan))

    n = max(len(x) for x, _, _ in tracks) + SR
    mix = np.zeros((n, 2))
    for x, gain, pan in tracks:
        st = np.stack([x * (1 - pan) / 2 + x / 2, x * (1 + pan) / 2 + x / 2], 1)
        mix[:len(x)] += gain * st

    # hall reverb (same design as make_audio.py)
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

    with wave.open('Cantique_sung_demo.wav', 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                    '-i', 'Cantique_sung_demo.wav',
                    '-codec:a', 'libmp3lame', '-q:a', '2', MP3], check=True)
    print('wrote', MP3)


if __name__ == '__main__':
    main()
