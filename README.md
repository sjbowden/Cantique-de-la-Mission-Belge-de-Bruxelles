# Cantique de la Mission Belge de Bruxelles

SATB hymn (Elder Matthew King; arr. Elder Robert Nakea, 1983; lyrics Sœur
Lynne Matthews) transcribed from the scanned sheet `IMG_1845.JPG`.

## Files
- `IMG_1845.JPG` — source photo of the printed hymn
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
- `Cantique.mp3` — generated audio rendition

## Audio rebuild
    pip install tinysoundfont mido numpy   # plus ffmpeg on the system
    python3 make_audio.py

## Editorial notes
Lyrics were normalized from the engraving: es-prit, très, sans, grâce,
Al-lons!, hon-nêtes, l'É-van-gi-le, Sœur; syllable splits corrected to sung
French (jus-qu'à, dé-cla-rons, dé-ses-pé-rons, se-ront, Pré-pa-rant,
deu-xi-ème). Accidentals verified against the scan: A-naturals in mm. 4, 7, 8;
B-naturals in m. 15.
