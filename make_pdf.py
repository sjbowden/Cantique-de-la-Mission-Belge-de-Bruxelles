#!/usr/bin/env python3
"""Render the MusicXML to print-ready one-page PDFs (US Letter and A4).

Requires:  pip install verovio cairosvg
Usage:     python3 gen_musicxml.py && python3 make_pdf.py
"""
import re

import verovio
import cairosvg

XML = 'Cantique_de_la_Mission_Belge_de_Bruxelles.musicxml'
PDF = 'Cantique_de_la_Mission_Belge_de_Bruxelles.pdf'
PDF_A4 = 'Cantique_de_la_Mission_Belge_de_Bruxelles_A4.pdf'
SVG = 'Cantique_de_la_Mission_Belge_de_Bruxelles.svg'
PNG = 'Cantique_preview.png'

# (output file, Verovio page w/h, output size in PostScript points)
FORMATS = [
    (PDF, 2159, 2794, 612, 792),           # US Letter
    (PDF_A4, 2100, 2970, 595.28, 841.89),  # A4
]


def render_page(page_w, page_h):
    tk = verovio.toolkit()
    tk.loadFile(XML)
    tk.setOptions({
        'pageWidth': page_w, 'pageHeight': page_h,
        'pageMarginLeft': 120, 'pageMarginRight': 120,
        'pageMarginTop': 60, 'pageMarginBottom': 60,
        'scale': 42,
        'breaks': 'encoded',        # honor the <print new-system> marks (4 systems)
        'justifyVertically': True,
        'header': 'encoded',        # use the <credit> blocks (title/authors)
        'footer': 'none',           # no 'engraved with Verovio' footer
        'lyricSize': 4.2,
        'spacingStaff': 7, 'spacingSystem': 10,
    })
    tk.redoLayout()
    assert tk.getPageCount() == 1, 'layout no longer fits one page'
    return tk.renderToSVG(1)


def style_header(svg):
    """Verovio renders every credit at a fixed 378px on one shared baseline,
    ignoring the MusicXML font-size/default-y hints. Restyle to match the
    original page: big title on its own line, smaller credits below it
    (composer over arranger at right, lyricist at left)."""
    svg, n = re.subn(r'font-size="\d+px">(Cantique de la Mission)',
                     r'font-size="560px">\1', svg)
    assert n == 1, 'title tspan not found'
    for name in ('Elder Matthew King', r'Arranged by Elder Robert Nakea \(1983\)',
                 'Sœur Lynne Matthews'):
        svg, n = re.subn(r'font-size="\d+px">(' + name + ')',
                         r'font-size="240px">\1', svg)
        assert n == 1, f'credit not found: {name}'
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
    return svg


for pdf, pw, ph, out_w, out_h in FORMATS:
    svg = style_header(render_page(pw, ph))
    cairosvg.svg2pdf(bytestring=svg.encode(), write_to=pdf,
                     output_width=out_w, output_height=out_h)
    if pdf == PDF:                  # the Letter render doubles as the preview
        open(SVG, 'w').write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=PNG,
                         output_width=1000)
    print(f'wrote {pdf}')
print(f'wrote {SVG}, {PNG}')
