#!/usr/bin/env python3
"""Generate per-voice karaoke MIDI files for eCantorix singing synthesis.

Writes Cantique_S.mid / _A.mid / _T.mid / _B.mid: one melody track each,
all three verses written out, with a MIDI text event carrying the French
syllable before every note (eCantorix convention). Melisma notes get the
vowel nucleus of the previous syllable so the vowel simply continues.

Requires: pip install mido
Usage:    python3 gen_sung_midi.py
"""
import re

import mido

import gen_musicxml as g   # note tables S/A/T/B, lyrics, parse()

BPM = 104
TPQ = 480                  # ticks per quarter; table divisions are eighths
TICKS_PER_DIV = TPQ // 2
VERSE_DIVS = 2 + 8 * 15 + 6
VERSES = 3

SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

# French vowel nucleus of a syllable, for melisma continuation notes
DIGRAPHS = ['eau', 'au', 'ou', 'oi', 'œu', 'eu', 'ai', 'ei', 'ui',
            'an', 'en', 'on', 'in', 'un']
VOWELS = 'aeiouyéèêëàâîïôûù'


def nucleus(syllable):
    s = re.sub(r"[^\wéèêëàâîïôûùœ']", '', syllable.lower()).rstrip("'")
    stripped = re.sub(r'es?$', '', s)
    if stripped and any(c in VOWELS for c in stripped):
        s = stripped                                   # drop mute final e/es
    best = None
    for i in range(len(s)):
        for d in DIGRAPHS:
            if s[i:i + len(d)] == d:
                best = d
        if s[i] in VOWELS and (best is None or all(
                s[j:j + len(dd)] != dd for j in range(i - 2, i + 1) if j >= 0
                for dd in DIGRAPHS)):
            if best is None or i > s.rfind(best):
                best = s[i]
    return best or 'a'


def midi_pitch(p):
    step, alter, octave, _ = g.parse(p)
    return 12 * (octave + 1) + SEMITONE[step] + alter


def syllable_onsets(verse):
    onsets, t = {}, 0
    for mn in range(1, 18):
        for i, (p, d) in enumerate(g.S[mn]):
            onsets[t] = g.LYR[mn][i][verse][0]
            t += d
    return onsets


def write_voice(name, table):
    mid = mido.MidiFile(ticks_per_beat=TPQ)
    tr = mido.MidiTrack()
    mid.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0))
    tr.append(mido.MetaMessage('track_name', name=name, time=0))

    events = []   # (tick, order, message-ish)
    for verse in range(VERSES):
        onsets = syllable_onsets(verse)
        t, last_syll = 0, ''
        for mn in range(1, 18):
            for p, d in table[mn]:
                if t in onsets:
                    syll = onsets[t]
                    last_syll = syll
                else:
                    syll = nucleus(last_syll)          # melisma continuation
                tick = (t + verse * VERSE_DIVS) * TICKS_PER_DIV
                dur = d * TICKS_PER_DIV - 10           # tiny release gap
                key = midi_pitch(p)
                events.append((tick, 0, ('text', syll)))
                events.append((tick, 1, ('on', key)))
                events.append((tick + dur, 2, ('off', key)))
                t += d
    events.sort(key=lambda e: (e[0], e[1]))

    now = 0
    for tick, _, ev in events:
        dt, now = tick - now, tick
        if ev[0] == 'text':
            # MIDI meta text is latin-1; espeak reads 'oe' the same as 'œ'
            tr.append(mido.MetaMessage('text', text=ev[1].replace('œ', 'oe'),
                                       time=dt))
        elif ev[0] == 'on':
            tr.append(mido.Message('note_on', note=ev[1], velocity=100, time=dt))
        else:
            tr.append(mido.Message('note_off', note=ev[1], velocity=0, time=dt))
    fn = f'Cantique_{name}.mid'
    mid.save(fn)
    print('wrote', fn)


for name, table in [('S', g.S), ('A', g.A), ('T', g.T), ('B', g.B)]:
    write_voice(name, table)
