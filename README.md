# Cantique de la Mission Belge de Bruxelles

SATB hymn (Elder Matthew King; arr. Elder Robert Nakea, 1983; lyrics Sœur
Lynne Matthews) transcribed from the scanned sheet `Cantique_original_scan.jpg`.

## Files
- `Cantique_original_scan.jpg` — source photo of the printed hymn
- `gen_musicxml.py` — the transcription itself: note tables (S/A/T/B per
  measure), all 3 verses of lyrics, and the MusicXML writer. Edit this to
  change any note or syllable, then re-run.
- `make_pdf.py` — renders the MusicXML to a one-page US-Letter PDF with the
  original page layout (title, author credits, 4 systems).
- `Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml` — generated score
  (opens in MuseScore / Finale / Sibelius)
- `Cantique_de_la_Mission_Belge_de_Bruxelles.pdf` — generated print PDF
- `Cantique_preview.png` — generated preview image

## Rebuild
    pip install verovio cairosvg
    python3 gen_musicxml.py
    python3 make_pdf.py

- `make_audio.py` — renders the hymn to audio (`Cantique.mp3`): choir +
  pipe organ layers from the GeneralUser GS soundfont (auto-downloaded),
  with phrasing, ritardando, and hall reverb.
- `Cantique.mp3` — generated audio rendition (all 3 verses)
- `gen_sung_musicxml.py` / `Cantique_sung.musicxml` — "singing edition":
  all 3 verses written out, four single-voice parts each carrying its own
  lyric line with melismas — the layout AI singing synthesizers expect
  (ACE Studio supports French today; MuseScore Studio's Cantai has French
  in development).

## Audio rebuild
    pip install tinysoundfont mido numpy   # plus ffmpeg on the system
    python3 make_audio.py

## Sung rendition (ISiS — IRCAM Singing Synthesis)
Real French singing voices sampled from real singers.
`gen_isis_scores.py` writes hand-phonetized X-SAMPA score files
(`Cantique_*.isis.cfg`, liaisons included); `make_isis_audio.py` renders
S=EL, A=MS, T/B=RT and mixes into `Cantique_sung_isis.mp3`.

    python3 gen_isis_scores.py && python3 make_isis_audio.py

### Getting ISiS
ISiS is free of charge for members of the IRCAM Forum (free account):

1. Register at https://forum.ircam.fr/ and open the ISiS project page
   (https://forum.ircam.fr/projects/detail/isis/).
2. Download the command-line application for your OS
   (`ISiS_V1.3.0_Linux_x86_64.tar.bz2` used here) and the three singing
   voice databases: EL (lyric soprano), MS (mezzo-soprano), RT (tenor) —
   about 0.7 GB each.
3. Unpack everything under `./ISiS/` in this repo (the engine folder plus
   `EL/`, `MS/`, `RT/` voice folders). The directory is gitignored: the
   software is licensed to your Forum account and must not be
   redistributed.

### Abandoned attempt: eCantorix (espeak + MBROLA)
We first tried the fully-open-source route — eCantorix driving espeak
with MBROLA French diphone voices (per-voice karaoke MIDIs, pitch
corrected via sox). It worked mechanically (pitches landed within ~20
cents after cancelling eCantorix's default two-octave transpose and
working around a pitch-calibration failure with the mb-fr1 voice), but
the result was judged unlistenable: speech diphones stretched onto held
notes with no vocal behavior. The scripts were removed in the commit
that added this note; see git history (`gen_sung_midi.py`,
`make_sung_audio.py`) if you ever want to revisit.

For commercial-grade quality, import `Cantique_sung.musicxml` into ACE Studio
(French supported) or MuseScore Studio's Cantai voices (French pending).

## Editorial notes
Lyrics were normalized from the engraving: es-prit, très, sans, grâce,
Al-lons!, hon-nêtes, l'É-van-gi-le, Sœur; syllable splits corrected to sung
French (jus-qu'à, dé-cla-rons, dé-ses-pé-rons, se-ront, Pré-pa-rant,
deu-xi-ème). Accidentals verified against the scan: A-naturals in mm. 4, 7, 8;
B-naturals in m. 15.
