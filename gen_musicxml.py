#!/usr/bin/env python3
"""Generate MusicXML for 'Cantique de la Mission Belge de Bruxelles'."""
from xml.sax.saxutils import escape

DIV = 2  # divisions per quarter

# (pitch, dur) ; pitch like 'Eb4', 'A4n' (explicit natural), dur in divisions
S = {
 1:[('Eb4',1),('G4',1)],
 2:[('Bb4',2),('Bb4',2),('Bb4',2),('C5',2)],
 3:[('Bb4',3),('Ab4',1),('G4',2),('Bb3',1),('D4',1)],
 4:[('Eb4',2),('Eb4',2),('F4',2),('G4',2)],
 5:[('F4',6),('Eb4',1),('G4',1)],
 6:[('Bb4',2),('Bb4',2),('Bb4',2),('C5',2)],
 7:[('Bb4',3),('Ab4',1),('G4',2),('G4',1),('A4n',1)],
 8:[('Bb4',2),('Bb4',2),('C5',2),('A4n',2)],
 9:[('Bb4',6),('Bb4',2)],
 10:[('Eb5',3),('D5',1),('C5',2),('Bb4',2)],
 11:[('C5',2),('Ab4',2),('G4',2),('G4',1),('Ab4',1)],
 12:[('Bb4',3),('Bb4',1),('C5',2),('G4',2)],
 13:[('F4',6),('Eb4',1),('G4',1)],
 14:[('Bb4',2),('Bb4',2),('Bb4',2),('C5',2)],
 15:[('Bb4',2),('Eb5',2),('Eb4',2),('Eb4',1),('F4',1)],
 16:[('G4',3),('F4',1),('C4',2),('D4',2)],
 17:[('Eb4',6)],
}
A = {
 1:[('Eb4',1),('G4',1)],
 2:[('G4',2),('G4',2),('G4',2),('Ab4',2)],
 3:[('G4',3),('F4',1),('Eb4',2),('Bb3',1),('Bb3',1)],
 4:[('C4',2),('C4',2),('C4',2),('Eb4',2)],
 5:[('D4',6),('Eb4',1),('G4',1)],
 6:[('Eb4',2),('Eb4',2),('G4',2),('Ab4',2)],
 7:[('G4',3),('F4',1),('Eb4',2),('G4',1),('Eb4',1)],
 8:[('G4',2),('G4',2),('G4',2),('F4',2)],
 9:[('Eb4',2),('C4',2),('D4',2),('F4',2)],
 10:[('Bb4',3),('Bb4',1),('Ab4',2),('G4',2)],
 11:[('Ab4',2),('F4',2),('Eb4',2),('G4',1),('Ab4',1)],
 12:[('G4',3),('G4',1),('G4',2),('Eb4',2)],
 13:[('D4',6),('Bb3',1),('Eb4',1)],
 14:[('G4',2),('G4',2),('G4',2),('Ab4',2)],
 15:[('G4',2),('G4',2),('C4',2),('B3n',1),('B3n',1)],
 16:[('Eb4',3),('Eb4',1),('Ab3',2),('Bb3',2)],
 17:[('Bb3',6)],
}
T = {
 1:[('Eb4',1),('Bb3',1)],
 2:[('Eb4',2),('Eb4',2),('Eb4',2),('Eb4',2)],
 3:[('Eb4',3),('Bb3',1),('Bb3',2),('Bb3',1),('Ab3',1)],
 4:[('G3',2),('G3',2),('F3',2),('F3',2)],
 5:[('Bb3',6),('Eb4',1),('Bb3',1)],
 6:[('G3',2),('G3',2),('Ab3',1),('Bb3',1),('C4',1),('D4',1)],
 7:[('Eb4',3),('D4',1),('Eb4',2),('G3',1),('C4',1)],
 8:[('D4',2),('D4',2),('Eb4',2),('C4',2)],
 9:[('Bb3',6),('D4',2)],
 10:[('Eb4',3),('Eb4',1),('Eb4',2),('Eb4',2)],
 11:[('Eb4',2),('F4',2),('Eb4',2),('D4',1),('C4',1)],
 12:[('D4',3),('D4',1),('Eb4',2),('C4',2)],
 13:[('Bb3',6),('G3',1),('Bb3',1)],
 14:[('Eb4',2),('Eb4',2),('Eb4',2),('Eb4',2)],
 15:[('D4',2),('Bb3',2),('G3',2),('G3',1),('Ab3',1)],
 16:[('Bb3',3),('Ab3',1),('F3',2),('Ab3',2)],
 17:[('G3',6)],
}
B = {
 1:[('Eb3',1),('Eb3',1)],
 2:[('Eb3',2),('Eb3',2),('Eb3',2),('Ab2',2)],
 3:[('Eb3',3),('Eb3',1),('Eb3',2),('Bb2',2)],
 4:[('C3',2),('C3',2),('Ab2',2),('A2n',2)],
 5:[('Bb2',6),('Eb3',1),('Eb3',1)],
 6:[('Eb3',2),('Eb3',2),('Eb3',2),('Eb3',2)],
 7:[('Eb3',3),('Bb2',1),('Eb3',2),('G3',1),('A3n',1)],
 8:[('G3',2),('G3',2),('C4',2),('F3',2)],
 9:[('Bb3',6),('Ab3',2)],
 10:[('G3',3),('G3',1),('Ab3',2),('Bb3',2)],
 11:[('C4',2),('D4',2),('Eb4',2),('D4',1),('C4',1)],
 12:[('G3',3),('G3',1),('C4',2),('F3',2)],
 13:[('Bb2',6),('Eb3',1),('Eb3',1)],
 14:[('Eb3',2),('Eb3',2),('Eb3',2),('Ab2',2)],
 15:[('G2',2),('G2',2),('C3',2),('B2n',1),('B2n',1)],
 16:[('Bb2',3),('Bb2',1),('Bb2',2),('Bb2',2)],
 17:[('Eb3',6)],
}

# lyrics: per measure, list of (v1,v2,v3) tuples aligned to S notes; syllabic codes:
# s=single b=begin m=middle e=end
LYR = {
 1:[(('1. Nous','s'),('2. Nous','s'),('3. En','s')), (('fai','b'),('dé','b'),('a','b'))],
 2:[(('sons','e'),('cla','m'),('vant!','e')), (('par','b'),('rons','e'),('Ne','s')),
    (('tie','e'),('à','s'),('dé','b')), (("d'une",'s'),('tout','s'),('ses','m'))],
 3:[(('grande','s'),('homme','s'),('pé','m')), (('ar','b'),('et','s'),('rons','e')),
    (('mée,','e'),('femme','s'),('point,','s')), (("c'est",'s'),('le','s'),('la','s')),
    (("l'ar",'b'),('bap','b'),('ba','b'))],
 4:[(('mée','e'),('tême,','e'),('taille','e')), (('du','s'),('la','s'),("n'est",'s')),
    (('Christ','s'),('re','b'),('pas','s')), (('le','s'),('pen','m'),('fi','b'))],
 5:[(('Roi;','s'),('tance,','e'),('nie;','e')), (('Nous','s'),('Car','s'),('Ceux','s')),
    (('a','b'),('no','b'),('qui','s'))],
 6:[(('vons','e'),('tre','e'),('sont','s')), (('son','s'),('Sei','b'),('fi','b')),
    (('es','b'),('gneur','e'),('dèles','e')), (('prit','e'),('dit','s'),('jus','b'))],
 7:[(('comme','s'),('que','s'),("qu'à",'e')), (('é','b'),('chaque','s'),('la','s')),
    (('pée,','e'),('âme','s'),('fin','s')), (('no','b'),('a','s'),('par','s')),
    (('tre','e'),('une','s'),('le','s'))],
 8:[(('bou','b'),('très','s'),('Christ','s')), (('cli','m'),('grande','s'),('se','b')),
    (('er,','e'),('im','b'),('ront','e')), (('la','s'),('por','m'),('bé','b'))],
 9:[(('foi!','s'),('tance.','e'),('nis.','e')), (('Nous','s'),('Nous','s'),('Al','b'))],
 10:[(('lut','b'),('té','b'),('lons!','e')), (('tons','e'),('moi','m'),('Que','s')),
     (('con','b'),('gnons','e'),('la','s')), (('tre','e'),('du','s'),('mois','b'))],
 11:[(('le','s'),('Christ','s'),('son','e')), (('pé','b'),('sans','s'),('com','b')),
     (('ché,','e'),('peur,','s'),('mence!','e')), (('re','b'),('de','s'),('Trou','b')),
     (('vê','m'),('sa','s'),('vons','e'))],
 12:[(('tus','e'),('grâce','s'),('les','s')), (('des','s'),('et','s'),('hon','b')),
     (('armes','s'),('son','s'),('nêtes','e')), (('de','s'),('sa','b'),('du','s'))],
 13:[(('Dieu,','s'),('lut,','e'),('cœur,','s')), (('Pour','s'),('Pré','b'),('Et','s')),
     (('que','s'),('pa','m'),('tra','b'))],
 14:[(("l'É",'b'),('rant','e'),('vail','m')), (('van','m'),('le','s'),('lons','e')),
     (('gi','m'),('monde','s'),('a','b')), (('le','e'),('pour','s'),('vec','e'))],
 15:[(('soit','s'),('le','s'),('di','b')), (('prê','b'),('bon','b'),('li','m')),
     (('ché','e'),('heur','e'),('gence','e')), (('à','s'),('de','s'),('pour','s')),
     (('chaque','s'),('sa','s'),('la','s'))],
 16:[(('homme','s'),('deu','b'),('gloi','b')), (('en','s'),('xi','m'),('re','e')),
     (('cha','b'),('ème','e'),('du','s')), (('que','e'),('ve','b'),('Sei','b'))],
 17:[(('lieu.','s'),('nue.','e'),('gneur.','e'))],
}

SYLL = {'s':'single','b':'begin','m':'middle','e':'end'}
STEP_ALTER = {'b':-1,'n':0,'':None}
KEY_FLATS = {'B','E','A'}  # flattened by key signature

def parse(p):
    step = p[0]; rest = p[1:]
    acc = ''
    if rest and rest[0] in 'bn':
        acc = rest[0]; rest = rest[1:]
    if rest and rest[-1] in 'bn':
        acc = rest[-1]; rest = rest[:-1]
    octave = int(rest)
    if acc == 'b': alter = -1
    elif acc == 'n': alter = 0
    else: alter = -1 if step in KEY_FLATS else 0
    # pitches written plain but in key-flat set are flat by key (we encoded all
    # flats explicitly as 'b', so plain B/E/A shouldn't occur)
    assert not (acc == '' and step in KEY_FLATS), f'ambiguous {p}'
    return step, alter, octave, acc

TYPES = {1:'eighth',2:'quarter',3:'quarter',4:'half',6:'half'}
DOTTED = {3,6}

def note_xml(p, dur, voice, staff, stem, lyrics=None, beam=None, chordless=True):
    step, alter, octave, acc = parse(p)
    o = ['<note>']
    o.append(f'<pitch><step>{step}</step>' +
             (f'<alter>{alter}</alter>' if alter else '') +
             f'<octave>{octave}</octave></pitch>')
    o.append(f'<duration>{dur}</duration>')
    o.append(f'<voice>{voice}</voice>')
    o.append(f'<type>{TYPES[dur]}</type>')
    if dur in DOTTED: o.append('<dot/>')
    if acc == 'n': o.append('<accidental>natural</accidental>')
    o.append(f'<stem>{stem}</stem>')
    o.append(f'<staff>{staff}</staff>')
    if beam: o.append(f'<beam number="1">{beam}</beam>')
    if lyrics:
        for i, (text, sy) in enumerate(lyrics, 1):
            o.append(f'<lyric number="{i}"><syllabic>{SYLL[sy]}</syllabic>'
                     f'<text>{escape(text)}</text></lyric>')
    o.append('</note>')
    return '\n'.join(o)

def beams_for(seq):
    """beam eighth-note runs in pairs (as engraved)."""
    out = [None]*len(seq)
    i = 0
    while i < len(seq):
        if seq[i][1] == 1 and i+1 < len(seq) and seq[i+1][1] == 1:
            out[i], out[i+1] = 'begin', 'end'
            i += 2
        else:
            i += 1
    return out

def build_part(upper, lower, clef_sign, clef_line, with_lyrics):
    """One single-staff part holding two voices (stems up / stems down)."""
    measures = []
    for mn in range(1, 18):
        mlen = sum(d for _, d in upper[mn])
        body = []
        if mn in (5, 9, 13):
            body.append('<print new-system="yes"/>')
        if mn == 1:
            body.append('<attributes><divisions>2</divisions>'
                        '<key><fifths>-3</fifths></key>'
                        '<time><beats>4</beats><beat-type>4</beat-type></time>'
                        f'<clef><sign>{clef_sign}</sign><line>{clef_line}</line></clef>'
                        '</attributes>')
        ub = beams_for(upper[mn])
        for i, (p, d) in enumerate(upper[mn]):
            lyr = LYR[mn][i] if with_lyrics else None
            body.append(note_xml(p, d, 1, 1, 'up', lyrics=lyr, beam=ub[i]))
        body.append(f'<backup><duration>{mlen}</duration></backup>')
        lb = beams_for(lower[mn])
        for i, (p, d) in enumerate(lower[mn]):
            body.append(note_xml(p, d, 2, 1, 'down', beam=lb[i]))
        implicit = ' implicit="yes"' if mn == 1 else ''
        barline = ('<barline location="right"><bar-style>light-heavy</bar-style></barline>'
                   if mn == 17 else '')
        measures.append(f'<measure number="{mn}"{implicit}>\n' +
                        '\n'.join(body) + barline + '\n</measure>')
    return chr(10).join(measures)

part1 = build_part(S, A, 'G', 2, with_lyrics=True)
part2 = build_part(T, B, 'F', 4, with_lyrics=False)

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work><work-title>Cantique de la Mission Belge de Bruxelles</work-title></work>
  <identification>
    <creator type="composer">Elder Matthew King</creator>
    <creator type="arranger">Arranged by Elder Robert Nakea (1983)</creator>
    <creator type="lyricist">Sœur Lynne Matthews</creator>
    <encoding><software>Transcribed from scanned image</software></encoding>
  </identification>
  <credit page="1"><credit-type>title</credit-type>
    <credit-words default-x="595" default-y="1550" justify="center" valign="top" font-weight="bold" font-size="60">Cantique de la Mission Belge de Bruxelles</credit-words></credit>
  <credit page="1"><credit-type>lyricist</credit-type>
    <credit-words default-x="85" default-y="1450" justify="left" valign="top" font-size="10">Sœur Lynne Matthews</credit-words></credit>
  <credit page="1"><credit-type>composer</credit-type>
    <credit-words default-x="1105" default-y="1470" justify="right" valign="top" font-size="10">Elder Matthew King</credit-words></credit>
  <credit page="1"><credit-type>arranger</credit-type>
    <credit-words default-x="1105" default-y="1440" justify="right" valign="top" font-size="10">Arranged by Elder Robert Nakea (1983)</credit-words></credit>
  <part-list>
    <part-group type="start" number="1">
      <group-symbol>brace</group-symbol>
      <group-barline>no</group-barline>
    </part-group>
    <score-part id="P1"><part-name></part-name></score-part>
    <score-part id="P2"><part-name></part-name></score-part>
    <part-group type="stop" number="1"/>
  </part-list>
  <part id="P1">
{part1}
  </part>
  <part id="P2">
{part2}
  </part>
</score-partwise>
'''
open('/home/sjbowden/hymn/Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml','w').write(xml)

# validation: per-voice duration sums
for mn in range(1,18):
    lens = {v: sum(d for _,d in V[mn]) for v,V in [('S',S),('A',A),('T',T),('B',B)]}
    assert len(set(lens.values()))==1, (mn,lens)
    assert len(LYR[mn]) == len(S[mn]), ('lyr', mn, len(LYR[mn]), len(S[mn]))
    for i,l in enumerate(LYR[mn]): assert len(l)==3, ('verses', mn, i)
print('OK: durations consistent, lyrics aligned;', sum(len(v) for v in S.values()), 'soprano notes')
