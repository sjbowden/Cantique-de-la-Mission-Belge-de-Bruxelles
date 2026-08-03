#!/usr/bin/env python3
"""Render the MusicXML to a print-ready one-page US-Letter PDF (+ preview PNG).

Requires:  pip install verovio cairosvg
Usage:     python3 gen_musicxml.py && python3 make_pdf.py
"""
import re

import verovio
import cairosvg

XML = 'Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml'
PDF = 'Cantique_de_la_Mission_Belge_de_Bruxelles.pdf'
SVG = 'Cantique_de_la_Mission_Belge_de_Bruxelles.svg'
PNG = 'Cantique_preview.png'

tk = verovio.toolkit()
tk.loadFile(XML)
tk.setOptions({
    'pageWidth': 2159, 'pageHeight': 2794,          # US Letter (Verovio units)
    'pageMarginLeft': 120, 'pageMarginRight': 120,
    'pageMarginTop': 60, 'pageMarginBottom': 60,
    'scale': 42,
    'breaks': 'encoded',            # honor the <print new-system> marks (4 systems)
    'justifyVertically': True,
    'header': 'encoded',            # use the <credit> blocks (title/authors)
    'footer': 'none',               # no 'engraved with Verovio' footer
    'lyricSize': 4.2,
    'spacingStaff': 7, 'spacingSystem': 10,
})
tk.redoLayout()
assert tk.getPageCount() == 1, 'layout no longer fits one page'
svg = tk.renderToSVG(1)

# --- Post-process the page header. Verovio renders every credit at a fixed
# 378px on one shared baseline, ignoring the MusicXML font-size/default-y
# hints, so restyle to match the original page: big title on its own line,
# smaller credits below it (composer over arranger at right, lyricist at left).
svg, n = re.subn(r'font-size="\d+px">(Cantique de la Mission)',
                 r'font-size="560px">\1', svg)
assert n == 1, 'title tspan not found'
for name in ('Elder Matthew King', r'Arranged by Elder Robert Nakea \(1983\)',
             'Sœur Lynne Matthews'):
    svg, n = re.subn(r'font-size="\d+px">(' + name + ')',
                     r'font-size="240px">\1', svg)
    assert n == 1, f'credit not found: {name}'
# reposition baselines (the first staff line sits at y=1179)
svg, n = re.subn(r'(class="rend"[^>]*?) y="\d+"([^>]*text-anchor="middle")',
                 r'\1 y="430"\2', svg)
assert n == 1, 'title rend not found'
svg, n = re.subn(r'(class="rend"[^>]*?) y="\d+"([^>]*text-anchor="start")',
                 r'\1 y="760"\2', svg)
assert n == 1, 'lyricist rend not found'
svg, n = re.subn(r'(class="rend"[^>]*?) y="2\d\d"([^>]*text-anchor="end")',
                 r'\1 y="760"\2', svg)
assert n == 1, 'composer rend not found'
svg, n = re.subn(r'(class="rend"[^>]*?) y="6\d\d"([^>]*text-anchor="end")',
                 r'\1 y="1000"\2', svg)
assert n == 1, 'arranger rend not found'

open(SVG, 'w').write(svg)
cairosvg.svg2pdf(bytestring=svg.encode(), write_to=PDF,
                 output_width=612, output_height=792)   # Letter, points
cairosvg.svg2png(bytestring=svg.encode(), write_to=PNG,
                 output_width=1000)
print(f'wrote {PDF}, {SVG}, {PNG}')
