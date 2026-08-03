#!/usr/bin/env python3
"""Generate a 'singing edition' MusicXML: Cantique_sung.musicxml.

All three verses written out in full (49 measures), four separate
single-voice parts (Soprano/Alto/Tenor/Bass), each with its own lyric
line. This is the layout AI singing synthesizers (ACE Studio,
Synthesizer V, Cantamus, ...) expect: one syllable stream per voice,
no verse stacks.

Syllables are mapped by onset: a note starting where the soprano
declaims a syllable gets that syllable; notes in between are melismas.
Usage: python3 gen_sung_musicxml.py   (after/with gen_musicxml.py)
"""
from xml.sax.saxutils import escape

import gen_musicxml as g   # note tables, lyrics, parse(), beams_for(), TYPES...

VERSE_DIVS = 2 + 8 * 15 + 6      # 128 divisions per verse
VERSES = 3


def flat_notes(table):
    """[(global_div, dur, pitch)] across the 3 written-out verses."""
    out = []
    for v in range(VERSES):
        t = v * VERSE_DIVS
        for mn in range(1, 18):
            for p, d in table[mn]:
                out.append((t, d, p))
                t += d
    return out


def syllable_onsets():
    """{global_div: (text, syllabic)} — verse v's words at verse v's pass."""
    onsets = {}
    for v in range(VERSES):
        t = v * VERSE_DIVS
        for mn in range(1, 18):
            for i, (p, d) in enumerate(g.S[mn]):
                text, sy = g.LYR[mn][i][v]
                onsets[t] = (text, sy)
                t += d
    return onsets


ONSETS = syllable_onsets()


def note_xml(p, dur, lyric):
    step, alter, octave, acc = g.parse(p)
    o = ['<note>']
    o.append(f'<pitch><step>{step}</step>' +
             (f'<alter>{alter}</alter>' if alter else '') +
             f'<octave>{octave}</octave></pitch>')
    o.append(f'<duration>{dur}</duration><voice>1</voice>')
    o.append(f'<type>{g.TYPES[dur]}</type>')
    if dur in g.DOTTED:
        o.append('<dot/>')
    if acc == 'n':
        o.append('<accidental>natural</accidental>')
    if lyric:
        text, sy = lyric
        o.append(f'<lyric number="1"><syllabic>{g.SYLL[sy]}</syllabic>'
                 f'<text>{escape(text)}</text></lyric>')
    o.append('</note>')
    return ''.join(o)


def build_part(table, clef_sign, clef_line):
    notes = flat_notes(table)
    total = VERSE_DIVS * VERSES
    # measure grid: 2-div pickup, then 8-div bars, 6-div final
    bounds = [0, 2] + list(range(10, total - 6 + 1, 8)) + [total]
    measures, ni = [], 0
    for mi in range(len(bounds) - 1):
        lo, hi = bounds[mi], bounds[mi + 1]
        body = []
        if mi == 0:
            body.append('<attributes><divisions>2</divisions>'
                        '<key><fifths>-3</fifths></key>'
                        '<time><beats>4</beats><beat-type>4</beat-type></time>'
                        f'<clef><sign>{clef_sign}</sign><line>{clef_line}</line></clef>'
                        '</attributes>')
        while ni < len(notes) and notes[ni][0] < hi:
            t, d, p = notes[ni]
            assert t + d <= hi, f'note crosses barline at div {t}'
            body.append(note_xml(p, d, ONSETS.get(t)))
            ni += 1
        implicit = ' implicit="yes"' if mi == 0 else ''
        barline = ('<barline location="right"><bar-style>light-heavy</bar-style>'
                   '</barline>' if mi == len(bounds) - 2 else '')
        measures.append(f'<measure number="{mi + 1}"{implicit}>' +
                        ''.join(body) + barline + '</measure>')
    assert ni == len(notes)
    return '\n'.join(measures)


PARTS = [('P1', 'Soprano', g.S, 'G', 2), ('P2', 'Alto', g.A, 'G', 2),
         ('P3', 'Tenor', g.T, 'F', 4), ('P4', 'Bass', g.B, 'F', 4)]

score_parts = '\n'.join(
    f'<score-part id="{pid}"><part-name>{name}</part-name></score-part>'
    for pid, name, *_ in PARTS)
parts = '\n'.join(
    f'<part id="{pid}">\n{build_part(tbl, cs, cl)}\n</part>'
    for pid, _, tbl, cs, cl in PARTS)

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work><work-title>Cantique de la Mission Belge de Bruxelles (singing edition, 3 verses)</work-title></work>
  <identification>
    <creator type="composer">Elder Matthew King</creator>
    <creator type="arranger">Arranged by Elder Robert Nakea (1983)</creator>
    <creator type="lyricist">Sœur Lynne Matthews</creator>
  </identification>
  <part-list>
{score_parts}
  </part-list>
{parts}
</score-partwise>
'''
open('Cantique_sung.musicxml', 'w').write(xml)
print('wrote Cantique_sung.musicxml')
