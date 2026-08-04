# Cantique de la Mission Belge de Bruxelles

*English version: [README.md](README.md)*

Cantique SATB (Elder Matthew King ; arr. Elder Robert Nakea, 1983 ; paroles de
Sœur Lynne Matthews), transcrit à partir de la partition numérisée
`Cantique_original_scan.jpg`.

## ⭐ L'essentiel
| | |
|---|---|
| 🎼 [**Partition imprimable (PDF, Lettre US)**](Cantique_de_la_Mission_Belge_de_Bruxelles.pdf) | une page, les 3 couplets |
| 🎼 [**Partition imprimable (PDF, A4)**](Cantique_de_la_Mission_Belge_de_Bruxelles_A4.pdf) | la même, pour papier A4 |
| 🎹 [**Enregistrement instrumental (MP3)**](Cantique_instrumental.mp3) | chœur « aah » + orgue, 3 couplets |
| 🎤 [**Enregistrement chanté (MP3)**](Cantique_sung.mp3) | quatre voix françaises de synthèse chantent les paroles |
| 📺 [**Interprétation de Wayne Shelton (YouTube)**](https://www.youtube.com/watch?v=y3b426utLxA) | une interprétation du cantique |

(Également téléchargeables depuis la [page Releases](../../releases).)

## Fichiers
- `Cantique_original_scan.jpg` — photo source du cantique imprimé
- `gen_musicxml.py` — la transcription elle-même : tables de notes (S/A/T/B
  par mesure), les 3 couplets de paroles, et le générateur MusicXML. À
  modifier pour corriger une note ou une syllabe, puis relancer.
- `make_pdf.py` — produit les PDF d'une page (Lettre US et A4) avec la mise
  en page d'origine (titre, crédits des auteurs, 4 systèmes).
- `Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml` — partition générée
  (s'ouvre dans MuseScore / Finale / Sibelius)
- `Cantique_de_la_Mission_Belge_de_Bruxelles.pdf` / `..._A4.pdf` — PDF
  d'impression générés (Lettre US et A4)
- `Cantique_preview.png` — image d'aperçu générée

## Regénérer
Le plus simple (crée automatiquement un `.venv` local, puis produit la
partition, les PDF, l'aperçu, le MP3 instrumental, l'édition chantée et
les partitions ISiS) :

    make            # ou : make sung / make everything / make clean / make distclean

Ou à la main :

    pip install verovio cairosvg pikepdf
    python3 gen_musicxml.py
    python3 make_pdf.py

Autre possibilité : tout installer dans un environnement virtuel local au
projet (recommandé sur les distributions dont le Python système est géré en
externe) :

    python3 -m venv .venv
    .venv/bin/pip install verovio cairosvg pikepdf mido numpy
    .venv/bin/pip install --no-deps tinysoundfont   # sa dépendance pyaudio ne sert qu'à la lecture en direct
    .venv/bin/python gen_musicxml.py && .venv/bin/python make_pdf.py

Le répertoire `.venv/` est ignoré par git ; utilisez `.venv/bin/python`
pour tous les scripts de ce dépôt.

- `make_audio.py` — rend le cantique en audio (`Cantique_instrumental.mp3`) :
  chœur + orgue superposés à partir de la banque de sons GeneralUser GS
  (téléchargée automatiquement), avec phrasé, ritardando et réverbération.
- `Cantique_instrumental.mp3` — rendu audio généré (les 3 couplets)
- `gen_sung_musicxml.py` / `Cantique_sung.musicxml` — « édition chantée » :
  les 3 couplets écrits en entier, quatre parties à voix unique portant
  chacune sa propre ligne de paroles avec mélismes — le format attendu par
  les synthétiseurs de chant (ACE Studio prend en charge le français ;
  le Cantai de MuseScore Studio l'annonce).

## Regénérer l'audio
    pip install tinysoundfont mido numpy   # plus ffmpeg sur le système
    python3 make_audio.py

## Version chantée (ISiS — synthèse de chant de l'IRCAM)
De vraies voix chantées françaises, échantillonnées sur de vrais chanteurs.
`gen_isis_scores.py` écrit des partitions phonétisées à la main en X-SAMPA
(`Cantique_*.isis.cfg`, liaisons comprises) ; `make_isis_audio.py` rend
S=EL, A=MS, T/B=RT et mixe le tout dans `Cantique_sung.mp3`. La basse
étant RT (un ténor) transposé sous sa tessiture, une variante sans la
partie de basse est aussi produite : `Cantique_sung_no_bass.mp3`.

    python3 gen_isis_scores.py && python3 make_isis_audio.py

### Obtenir ISiS
ISiS est gratuit pour les membres du Forum IRCAM (compte gratuit) :

1. S'inscrire sur https://forum.ircam.fr/ puis ouvrir la page du projet ISiS
   (https://forum.ircam.fr/projects/detail/isis/).
2. Télécharger l'application en ligne de commande pour votre système
   (`ISiS_V1.3.0_Linux_x86_64.tar.bz2` utilisée ici) ainsi que les trois
   bases de voix chantées : EL (soprano lyrique), MS (mezzo-soprano),
   RT (ténor) — environ 0,7 Go chacune.
3. Tout décompresser sous `./ISiS/` dans ce dépôt (le dossier du moteur plus
   les dossiers de voix `EL/`, `MS/`, `RT/`). Le répertoire est ignoré par
   git : le logiciel est licencié à votre compte Forum et ne doit pas être
   redistribué.

### Dépannage : « Intel MKL FATAL ERROR: Cannot load libmkl_def.so »
Le paquet ISiS omet le noyau CPU générique de MKL ; les processeurs que
MKL y dirige (notamment AMD) plantent pendant la synthèse. Correction :

    make isis-mkl-fix

qui fait pointer les `libmkl_def.so` / `libmkl_vml_def.so` manquants
vers les noyaux AVX2 fournis (cibles équivalentes ; tout processeur AMD
moderne a AVX2).

### Tentative abandonnée : eCantorix (espeak + MBROLA)
Nous avons d'abord essayé la voie entièrement libre — eCantorix pilotant
espeak avec les voix de diphones français MBROLA (fichiers MIDI karaoké par
voix, hauteur corrigée par sox). Mécaniquement, cela fonctionnait (justesse
à ~20 cents près, après annulation de la transposition par défaut de deux
octaves d'eCantorix et contournement d'un échec de calibration de hauteur
avec la voix mb-fr1), mais le résultat a été jugé inécoutable : des diphones
de parole étirés sur des notes tenues, sans aucun comportement vocal. Les
scripts ont été supprimés dans le commit qui a ajouté cette note ; voir
l'historique git (`gen_sung_midi.py`, `make_sung_audio.py`) pour y revenir.

Pour une qualité professionnelle, importer `Cantique_sung.musicxml` dans
ACE Studio (français pris en charge) ou dans les voix Cantai de MuseScore
Studio (français en cours de développement).

## Reproductibilité
Les regénérations sont identiques à l'octet près sur une même machine
(identifiants XML de Verovio initialisés par une graine ; PDF normalisés
avec pikepdf, dates supprimées). Sur une machine *différente*, les PDF
et MP3 regénérés peuvent différer octet par octet tout en ayant un
contenu identique — les polices incorporées et la version de l'encodeur
LAME varient d'un système à l'autre. Si `git status` montre des fichiers
générés comme modifiés après une compilation sans changement des
sources, faites simplement `git restore` ; ne validez des sorties
regénérées que si la musique, les paroles ou le rendu ont réellement
changé.

## Notes éditoriales
Les paroles ont été normalisées par rapport à la gravure : es-prit, très,
sans, grâce, Al-lons !, hon-nêtes, l'É-van-gi-le, Sœur ; les coupes
syllabiques ont été corrigées selon le chant (jus-qu'à, dé-cla-rons,
dé-ses-pé-rons, se-ront, Pré-pa-rant, deu-xi-ème). Altérations vérifiées
sur la numérisation : la bécarre aux mesures 4, 7 et 8 ; si bécarre à la
mesure 15.
