#!/usr/bin/env python3
"""Generate ISiS score files (one per SATB voice, all three verses).

ISiS (IRCAM Singing Synthesis) takes X-SAMPA phonemes plus midiNotes /
rhythm / tempo. Alignment is one vowel per note, so each voice's stream
must contain exactly as many vowels as it has notes. Melisma notes get
the held vowel again, with the syllable's coda consonants moved to the
last note of the group.

The phoneme lists below are hand-written French X-SAMPA aligned to the
soprano's 63 syllables per verse, including sung liaisons (son‿esprit,
des‿armes, tout‿homme, les‿honnêtes, En‿avant) and resyllabification
across notes (chaque homme -> S a | k O m, grande ar- -> g R a~ | d a R).

Usage: python3 gen_isis_scores.py
"""
import gen_musicxml as g

BPM = 104
VERSES = 3

# X-SAMPA per soprano syllable, in LYR order (m1..m17), one list per verse.
P1 = [
    'n u', 'f 2',                                    # m1  Nous fai-
    'z o~', 'p a R', 't i', 'd y n',                 # m2  sons par-tie d'une
    'g R a~', 'd a R', 'm e', 's E', 'l a R',        # m3  grande ar-mée, c'est l'ar-
    'm e', 'd y', 'k R i s t', 'l @',                # m4  mée du Christ le
    'R w a', 'n u', 'z a',                           # m5  Roi; Nous a- (nous_avons)
    'v o~', 's o~', 'n E s', 'p R i',                # m6  vons son es-prit (son_esprit)
    'k O m', 'e', 'p e', 'n O', 't R @',             # m7  comme é-pée, no-tre
    'b u', 'k l i', 'e', 'l a',                      # m8  bou-cli-er, la
    'f w a', 'n u',                                  # m9  foi! Nous
    'l y', 't o~', 'k o~', 't R @',                  # m10 lut-tons con-tre
    'l @', 'p e', 'S e', 'R @', 'v E',               # m11 le pé-ché, re-vê-
    't y', 'd e', 'z a R m', 'd @',                  # m12 tus des armes de (des_armes)
    'd j 2', 'p u R', 'k @',                         # m13 Dieu, Pour que
    'l e', 'v a~', 'Z i', 'l @',                     # m14 l'É-van-gi-le
    's w a', 'p R E', 'S e', 'a', 'S a',             # m15 soit prê-ché à chaque
    'k O', 'm a~', 'S a', 'k @',                     # m16 homme en cha-que
    'l j 2',                                         # m17 lieu.
]
P2 = [
    'n u', 'd e',                                    # m1  Nous dé-
    'k l a', 'R o~', 'a', 't u',                     # m2  cla-rons à tout
    't O', 'm e', 'f a m', 'l @', 'b a',             # m3  homme et femme le bap- (tout_homme, homme_et)
    't E m', 'l a', 'R @', 'p a~',                   # m4  tême, la re-pen-
    't a~ s', 'k a R', 'n O',                        # m5  tance, Car no-
    't R @', 's E', 'N 9 R', 'd i',                  # m6  tre Sei-gneur dit
    'k @', 'S a', 'k a m', 'a', 'y n',               # m7  que chaque âme a une (chaque_âme)
    't R E', 'g R a~', 'd e~', 'p O R',              # m8  très grande im-por- (grande_im)
    't a~ s', 'n u',                                 # m9  tance. Nous
    't e', 'm w a', 'N o~', 'd y',                   # m10 té-moi-gnons du
    'k R i s t', 's a~', 'p 9 R', 'd @', 's a',      # m11 Christ sans peur, de sa
    'g R a s', 'e', 's o~', 's a',                   # m12 grâce et son sa-
    'l y', 'p R e', 'p a',                           # m13 lut, Pré-pa-
    'R a~', 'l @', 'm o~ d', 'p u R',                # m14 rant le monde pour
    'l @', 'b o~', 'n 9 R', 'd @', 's a',            # m15 le bon-heur de sa
    'd 2', 'z j E', 'm @', 'v @',                    # m16 deu-xi-ème ve-
    'n y',                                           # m17 nue.
]
P3 = [
    'a~', 'n a',                                     # m1  En a- (En_avant)
    'v a~', 'n @', 'd e', 'z E s',                   # m2  vant! Ne dé-ses- (dé.zɛs)
    'p e', 'R o~', 'p w e~', 'l a', 'b a',           # m3  pé-rons point, la ba-
    't a j', 'n E', 'p a', 'f i',                    # m4  taille n'est pas fi-
    'n i', 's 2', 'k i',                             # m5  nie; Ceux qui
    's o~', 'f i', 'd E l', 'Z y s',                 # m6  sont fi-dèles jus-
    'k a', 'l a', 'f e~', 'p a R', 'l @',            # m7  qu'à la fin par le
    'k R i s t', 's @', 'R o~', 'b e',               # m8  Christ se-ront bé-
    'n i', 'a',                                      # m9  nis. Al-
    'l o~', 'k @', 'l a', 'm w a',                   # m10 lons! Que la mois-
    's o~', 'k o~', 'm a~ s', 't R u', 'v o~',       # m11 son com-mence! Trou-vons
    'l e', 'z O', 'n E t', 'd y',                    # m12 les hon-nêtes du (les_honnêtes)
    'k 9 R', 'e', 't R a',                           # m13 cœur, Et tra-
    'v a', 'j o~', 'a', 'v E k',                     # m14 vail-lons a-vec
    'd i', 'l i', 'Z a~ s', 'p u R', 'l a',          # m15 di-li-gence pour la
    'g l w a', 'R @', 'd y', 's E',                  # m16 gloi-re du Sei-
    'N 9 R',                                         # m17 gneur.
]
PHON = [P1, P2, P3]

VOWELS = {'a', 'e', 'E', '2', '9', '@', 'i', 'o', 'O', 'u', 'y',
          'o~', 'a~', 'e~', '9~'}


def split_syllable(x):
    """-> (onset tokens, vowel token, coda tokens)"""
    toks = x.split()
    vi = next(i for i, t in enumerate(toks) if t in VOWELS)
    return toks[:vi], toks[vi], toks[vi + 1:]


def verse_onsets(verse):
    """{div_in_verse: syllable index} from the soprano rhythm."""
    onsets, t, k = {}, 0, 0
    for mn in range(1, 18):
        for p, d in g.S[mn]:
            onsets[t] = k
            k += 1
            t += d
    return onsets


def voice_stream(table, verse):
    """[(midinote, dur_quarters, xsampa-for-this-note)] for one verse."""
    onsets = verse_onsets(verse)
    phon = PHON[verse]
    # collect notes with their syllable index (or None for melisma)
    notes, t = [], 0
    for mn in range(1, 18):
        for p, d in table[mn]:
            step, alter, octv, _ = g.parse(p)
            midi = 12 * (octv + 1) + \
                {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[step] + alter
            notes.append([midi, d / 2.0, onsets.get(t)])
            t += d
    # group melismas and distribute onset/vowel/coda
    out, i = [], 0
    while i < len(notes):
        midi, dur, si = notes[i]
        assert si is not None or i == 0, f'melisma at stream start ({i})'
        j = i + 1
        while j < len(notes) and notes[j][2] is None:
            j += 1
        onset, vowel, coda = split_syllable(phon[si])
        group = notes[i:j]
        for k, (m, dd, _) in enumerate(group):
            parts = []
            if k == 0:
                parts += onset
            parts.append(vowel)
            if k == len(group) - 1:
                parts += coda
            out.append((m, dd, ' '.join(parts)))
        i = j
    return out


def build_score(table, transp_comment=''):
    xs, notes, rhy = ['_'], [0], [1.0]
    for verse in range(VERSES):
        for midi, dur, x in voice_stream(table, verse):
            xs.append(x)
            notes.append(midi)
            rhy.append(dur)
    xs.append('_')
    notes.append(0)
    rhy.append(2.0)
    n_vowels = sum(1 for x in xs for t in x.split() if t in VOWELS)
    assert n_vowels == len(notes) - 2, (n_vowels, len(notes))
    return (f'[lyrics]\nxsampa: {" ".join(xs)}\n\n[score]\n'
            f'midiNotes: {", ".join(str(n) for n in notes)}\n'
            f'rhythm: {", ".join(f"{r:g}" for r in rhy)}\n'
            f'{transp_comment}globalTransposition: 0\n'
            f'defaultSentenceLoudness: 0.5\ntempo: {BPM}\n')


for part, table in [('S', g.S), ('A', g.A), ('T', g.T), ('B', g.B)]:
    fn = f'Cantique_{part}.isis.cfg'
    open(fn, 'w').write(build_score(table))
    print('wrote', fn)

# review aid: syllable/phoneme table
for v in range(VERSES):
    texts = [LYR_txt for mn in range(1, 18) for LYR_txt, *_ in
             (lyr[v] for lyr in g.LYR[mn])]
    assert len(texts) == len(PHON[v]) == 63, (v, len(texts), len(PHON[v]))
print('verse syllable counts OK (63 each)')
