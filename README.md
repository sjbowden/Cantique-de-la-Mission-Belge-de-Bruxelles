# Cantique de la Mission Belge de Bruxelles

*Version française : [README.fr.md](README.fr.md)*

SATB hymn (Elder Matthew King; arr. Elder Robert Nakea, 1983; lyrics Sœur
Lynne Matthews) transcribed from the scanned sheet `Cantique_original_scan.jpg`.

## ⭐ The good stuff
| | |
|---|---|
| 🎼 [**Printable sheet music (PDF, US Letter)**](Cantique_de_la_Mission_Belge_de_Bruxelles.pdf) | one page, all 3 verses |
| 🎼 [**Printable sheet music (PDF, A4)**](Cantique_de_la_Mission_Belge_de_Bruxelles_A4.pdf) | same, for A4 paper |
| 🎹 [**Instrumental recording (MP3)**](Cantique_instrumental.mp3) | pipe organ + soft strings, 3 verses |
| 🎤 [**Sung recording (MP3)**](Cantique_sung.mp3) | four synthesized French voices singing the lyrics |
| 📺 [**Wayne Shelton's rendition (YouTube)**](https://www.youtube.com/watch?v=y3b426utLxA) | a performance of the hymn |

(Also available as downloads on the [Releases page](../../releases).)

## Files
- `Cantique_original_scan.jpg` — source photo of the printed hymn
- `gen_musicxml.py` — the transcription itself: note tables (S/A/T/B per
  measure), all 3 verses of lyrics, and the MusicXML writer. Edit this to
  change any note or syllable, then re-run.
- `make_pdf.py` — renders the MusicXML to a one-page US-Letter PDF with the
  original page layout (title, author credits, 4 systems).
- `Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml` — generated score
  (opens in MuseScore / Finale / Sibelius)
- `Cantique_de_la_Mission_Belge_de_Bruxelles.pdf` / `..._A4.pdf` — generated
  print PDFs (US Letter and A4)
- `Cantique_preview.png` — generated preview image

## Rebuild
The simplest way (creates a local `.venv` automatically, builds score,
PDFs, preview, instrumental MP3, singing edition, and ISiS score files):

    make            # or: make sung / make everything / make clean / make distclean

Or by hand:

    pip install verovio cairosvg pikepdf
    python3 gen_musicxml.py
    python3 make_pdf.py

Alternatively, keep everything in a project-local virtual environment
(recommended on distros whose system Python is externally managed):

    python3 -m venv .venv
    .venv/bin/pip install verovio cairosvg pikepdf mido numpy
    .venv/bin/pip install --no-deps tinysoundfont   # its pyaudio dep is only for live playback
    .venv/bin/python gen_musicxml.py && .venv/bin/python make_pdf.py

The `.venv/` directory is gitignored; use `.venv/bin/python` for any of the
scripts in this repo.

- `make_audio.py` — renders the hymn to audio (`Cantique_instrumental.mp3`):
  pipe organ (with 16' pedal) and soft strings from the GeneralUser GS soundfont
  (auto-downloaded), with phrasing, ritardando, and hall reverb.
- `Cantique_instrumental.mp3` — generated audio rendition (all 3 verses)
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
S=EL, A=MS, T/B=RT and mixes into `Cantique_sung.mp3`. Because the
bass is RT (a tenor) transposed below his range, a variant without
the bass part is also produced: `Cantique_sung_no_bass.mp3`.

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

### Troubleshooting: MKL errors on non-Intel CPUs
On AMD (and other non-Intel) processors, ISiS synthesis dies with

    Intel MKL FATAL ERROR: Cannot load libmkl_def.so.

or, if a substitute kernel is offered under that name,

    Intel MKL WARNING: Library libmkl_def.so (MKL type 5) is not
    suitable for this processor (MKL type 0).

The ISiS bundle omits MKL's generic CPU kernel, and this MKL routes all
non-Intel processors to it. Fix with

    make isis-mkl-fix

which compiles a tiny LD_PRELOAD shim (requires `cc`) making MKL's
Intel-CPU check return true, so it dispatches the bundled AVX2 kernel
instead of demanding the missing generic one. Any modern AMD CPU has
AVX2. (Linking libmkl_def.so to the AVX2 kernel does not work: this MKL
validates kernel "types" and rejects the substitute.)

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

## Reproducibility
Rebuilds are byte-identical on the same machine (Verovio's XML IDs are
seeded; the PDFs are normalized with pikepdf, dates stripped). On a
*different* machine, rebuilt PDFs and MP3s may differ byte-wise while
being content-identical — embedded font files and the LAME encoder
version vary between systems. If `git status` shows generated outputs
as modified after a build and you didn't change any source, just
`git restore` them; only commit refreshed outputs when the music,
lyrics, or rendering actually changed.

## Editorial notes
Lyrics were normalized from the engraving: es-prit, très, sans, grâce,
Al-lons!, hon-nêtes, l'É-van-gi-le, Sœur; syllable splits corrected to sung
French (jus-qu'à, dé-cla-rons, dé-ses-pé-rons, se-ront, Pré-pa-rant,
deu-xi-ème). Accidentals verified against the scan: A-naturals in mm. 4, 7, 8;
B-naturals in m. 15.
