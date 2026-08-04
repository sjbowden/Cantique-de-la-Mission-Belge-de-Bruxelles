# Build all generated pieces of the Cantique repo.
#
#   make            - score, PDFs, preview, instrumental MP3, singing edition
#   make sung       - the ISiS sung MP3s (requires ./ISiS/, see README)
#   make everything - all of the above
#   make clean      - remove intermediate files (kept out of git anyway)
#   make distclean  - also remove all generated outputs, the venv, and the
#                     downloaded soundfont (leaves only sources + ISiS)
#
# Requires GNU make >= 4.3 (grouped targets) and python3 with venv.

PY  := .venv/bin/python
PIP := .venv/bin/pip

SCORE    := Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml
PDF      := Cantique_de_la_Mission_Belge_de_Bruxelles.pdf
PDF_A4   := Cantique_de_la_Mission_Belge_de_Bruxelles_A4.pdf
SVG      := Cantique_de_la_Mission_Belge_de_Bruxelles.svg
PREVIEW  := Cantique_preview.png
INSTR    := Cantique_instrumental.mp3
SUNG_XML := Cantique_sung.musicxml
ISISCFGS := Cantique_S.isis.cfg Cantique_A.isis.cfg \
            Cantique_T.isis.cfg Cantique_B.isis.cfg
SUNG_MP3 := Cantique_sung.mp3 Cantique_sung_no_bass.mp3

.PHONY: all everything sung clean distclean
all: $(SCORE) $(PDF) $(PDF_A4) $(PREVIEW) $(INSTR) $(SUNG_XML) $(ISISCFGS)
everything: all sung
sung: $(SUNG_MP3)

# --- environment -----------------------------------------------------------
.venv/.stamp:
	python3 -m venv .venv
	$(PIP) install verovio cairosvg pikepdf mido numpy
	$(PIP) install --no-deps tinysoundfont  # its pyaudio dep is playback-only
	touch $@

# --- pieces ----------------------------------------------------------------
$(SCORE): gen_musicxml.py .venv/.stamp
	$(PY) gen_musicxml.py

$(PDF) $(PDF_A4) $(SVG) $(PREVIEW) &: make_pdf.py $(SCORE)
	$(PY) make_pdf.py

$(INSTR): make_audio.py gen_musicxml.py .venv/.stamp
	$(PY) make_audio.py

$(SUNG_XML): gen_sung_musicxml.py gen_musicxml.py .venv/.stamp
	$(PY) gen_sung_musicxml.py

$(ISISCFGS) &: gen_isis_scores.py gen_musicxml.py .venv/.stamp
	$(PY) gen_isis_scores.py

$(SUNG_MP3) &: make_isis_audio.py $(ISISCFGS)
	@test -d ISiS || { echo 'ISiS not installed - see README "Getting ISiS"'; exit 1; }
	$(PY) make_isis_audio.py

# ISiS bundles Intel MKL without its generic CPU kernel (libmkl_def.so).
# CPUs that MKL dispatches to that kernel (notably AMD) crash with
# "Cannot load libmkl_def.so". The bundled kernels are interchangeable
# dispatch targets, so point the missing ones at the AVX2 versions
# (any modern AMD CPU has AVX2).
.PHONY: isis-mkl-fix
isis-mkl-fix:
	cd ISiS/ISiS_V*/ISiS/_internal && \
	  ln -sf libmkl_avx2.so libmkl_def.so && \
	  ln -sf libmkl_vml_avx2.so libmkl_vml_def.so
	@echo "MKL def kernels linked to AVX2 - retry: make sung"

# --- cleaning --------------------------------------------------------------
clean:
	rm -f Cantique_instrumental.wav Cantique_sung.wav Cantique_sung_no_bass.wav
	rm -f isis_S.wav isis_A.wav isis_T.wav isis_B.wav isis_*.log
	rm -rf __pycache__

distclean: clean
	rm -f $(SCORE) $(PDF) $(PDF_A4) $(SVG) $(PREVIEW)
	rm -f $(INSTR) $(SUNG_XML) $(ISISCFGS) $(SUNG_MP3)
	rm -f GeneralUserGS.sf2
	rm -rf .venv
