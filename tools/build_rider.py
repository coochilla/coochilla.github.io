"""Build the downloadable rider and matching SVG/PDF stage plot."""
from pathlib import Path
import html
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'site' / 'assets'
INK = colors.HexColor('#171717')
PAPER = colors.HexColor('#eee9de')
ORANGE = colors.HexColor('#ff4c26')
GRAY = colors.HexColor('#bcb6ab')
W, H = A4
M = 43
WIDTH = W - M * 2
P = ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, textColor=INK)

POSITIONS = [
    (35, 60, 215, 85, 'BASS', 'No vocal', 'Ch 3 | + ch 4 in amp mode', True),
    (290, 60, 215, 85, 'DRUMS', 'No vocal', 'Ch 8-13 | six-mic basic setup', False),
    (20, 195, 150, 90, 'GUITAR LEFT', 'Backing vocal', 'Instrument ch 1 | vocal ch 6', True),
    (195, 195, 150, 90, 'LEAD SINGER', 'Lead vocal', 'Vocal ch 5', False),
    (370, 195, 150, 90, 'GUITAR RIGHT', 'Backing vocal', 'Instrument ch 2 | vocal ch 7', True),
]

def plot_pdf(c, x, y, width):
    scale = width / 540
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    c.setFillColor(PAPER)
    c.setStrokeColor(GRAY)
    c.rect(0, 0, 540, 355, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(270, 329, 'UPSTAGE / BACK')
    c.setFont('Helvetica', 9)
    c.drawCentredString(270, 312, 'Viewed from the audience - positions are not to scale')
    for left, top, width_, height, title, vocal, feed, power in POSITIONS:
        bottom = 355 - top - height
        c.setFillColor(colors.white)
        c.setStrokeColor(INK)
        c.roundRect(left, bottom, width_, height, 4, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(left + width_ / 2, bottom + height - 25, title)
        c.setFont('Helvetica', 10)
        c.drawCentredString(left + width_ / 2, bottom + height - 45, vocal)
        c.setFont('Helvetica', 8.5)
        c.drawCentredString(left + width_ / 2, bottom + 17, feed)
        if power:
            c.setFillColor(ORANGE)
            c.rect(left + width_ - 18, bottom + height - 18, 14, 14, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont('Helvetica-Bold', 8)
            c.drawCentredString(left + width_ - 11, bottom + height - 14, 'P')
    c.setFillColor(INK)
    c.setFont('Helvetica', 8.5)
    c.drawCentredString(270, 181, 'P = mains power at the instrument rigs')
    c.drawString(20, 46, 'Audience left = stage right')
    c.drawRightString(520, 46, 'Audience right = stage left')
    c.setStrokeColor(ORANGE)
    c.setLineWidth(3)
    c.line(20, 32, 520, 32)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(270, 13, 'AUDIENCE / FRONT OF STAGE')
    c.restoreState()
    return width * 355 / 540

def svg_plot():
    pieces = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 355" role="img" aria-labelledby="title desc">',
        '<title id="title">Coochilla stage plot, viewed from the audience</title>',
        '<desc id="desc">Bass back-left and drums back-right, neither singing. Guitar left with backing vocal, lead singer center and guitar right with backing vocal at the front. Guitar channels 1 and 2; bass channel 3 plus channel 4 in amp mode; vocals 5 to 7; drums 8 to 13. P marks mains power.</desc>',
        '<rect width="540" height="355" fill="#eee9de" stroke="#bcb6ab"/>',
        '<g fill="#171717" font-family="Arial,Helvetica,sans-serif" text-anchor="middle">',
        '<text x="270" y="26" font-size="10" font-weight="700">UPSTAGE / BACK</text>',
        '<text x="270" y="43" font-size="9">Viewed from the audience - positions are not to scale</text>']
    for left, top, width, height, title, vocal, feed, power in POSITIONS:
        pieces += [f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="4" fill="#fff" stroke="#171717"/>',
            f'<text x="{left + width / 2}" y="{top + 25}" font-size="12" font-weight="700">{html.escape(title)}</text>',
            f'<text x="{left + width / 2}" y="{top + 45}" font-size="10">{html.escape(vocal)}</text>',
            f'<text x="{left + width / 2}" y="{top + height - 17}" font-size="8.5">{html.escape(feed)}</text>']
        if power:
            pieces += [f'<rect x="{left + width - 18}" y="{top + 4}" width="14" height="14" fill="#ff4c26"/>',
                f'<text x="{left + width - 11}" y="{top + 14}" font-size="8" font-weight="700">P</text>']
    pieces += ['<text x="270" y="174" font-size="8.5">P = mains power at the instrument rigs</text>',
        '<text x="20" y="309" text-anchor="start" font-size="8.5">Audience left = stage right</text>',
        '<text x="520" y="309" text-anchor="end" font-size="8.5">Audience right = stage left</text>',
        '<path d="M20 323H520" stroke="#ff4c26" stroke-width="3"/>',
        '<text x="270" y="342" font-size="10" font-weight="700">AUDIENCE / FRONT OF STAGE</text></g></svg>']
    return '\n'.join(pieces)

def base(c, subtitle, page, total):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 30)
    c.drawString(M, H - 67, 'COOCHILLA')
    c.setFont('Helvetica', 10)
    c.drawString(M, H - 87, subtitle)
    c.setStrokeColor(ORANGE)
    c.setLineWidth(3)
    c.line(M, H - 102, W - M, H - 102)
    c.setStrokeColor(GRAY)
    c.setLineWidth(.5)
    c.line(M, 45, W - M, 45)
    c.setFillColor(INK)
    c.setFont('Helvetica', 8)
    c.drawString(M, 30, 'Hector | bahamondeh@gmail.com | Updated 29 October 2026')
    c.drawRightString(W - M, 30, f'{page} / {total}')

def para(c, text, y, width=WIDTH, size=10, leading=14):
    style = ParagraphStyle('paragraph', parent=P, fontSize=size, leading=leading)
    p = Paragraph(text, style)
    _, height = p.wrap(width, H)
    p.drawOn(c, M, y - height)
    return y - height - 10

def heading(c, text, y):
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(M, y - 13, text)
    return y - 24

def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / 'coochilla-stage-plot.svg').write_text(svg_plot(), encoding='utf-8')
    plot = canvas.Canvas(str(ASSETS / 'coochilla-stage-plot.pdf'), pagesize=A4)
    plot.setTitle('Coochilla - Stage plot')
    plot.setAuthor('Coochilla')
    base(plot, 'STAGE PLOT | European Summer Tour - June 2027', 1, 1)
    ph = WIDTH * 355 / 540
    y = H - 125 - ph
    plot_pdf(plot, M, y, WIDTH)
    y -= 20
    y = para(plot, '<b>Front:</b> guitar left + backing vocal; lead singer center; guitar right + backing vocal.', y)
    y = para(plot, '<b>Back:</b> bass on audience-left; drums on audience-right. Neither bass nor drums has a vocal mic.', y)
    y = para(plot, '<b>P = power:</b> mains power at both guitar rigs and the bass rig. Monitoring positions and mix allocation are agreed with the venue.', y)
    y = para(plot, '<b>IR mode:</b> one mono DI / IR channel per instrument: guitar left, guitar right and bass. Three instrument channels total; no cabinet mics.', y)
    y = para(plot, '<b>Amp mode:</b> one mic per guitar cabinet and one mic on the bass cabinet, plus a separate bass IR feed. Four instrument channels total. Suitable cabinets and amplification are agreed in advance.', y)
    y = para(plot, '<b>Basic drums:</b> kick, snare top, rack tom, floor tom and stereo overheads (six microphones). See the technical rider for the full patch.', y)
    assert y > 55
    plot.save()

    rider = canvas.Canvas(str(ASSETS / 'coochilla-technical-rider.pdf'), pagesize=A4)
    rider.setTitle('Coochilla - Technical rider and stage plot')
    rider.setAuthor('Coochilla')
    base(rider, 'TECHNICAL RIDER | European Summer Tour - June 2027', 1, 2)
    y = para(rider, '<b>Five musicians / three vocal positions.</b> Both guitarists sing backing vocals; the central singer handles lead vocals. Bass and drums do not sing.', H - 120)
    ph = WIDTH * 355 / 540
    y -= ph
    plot_pdf(rider, M, y, WIDTH)
    y -= 18
    y = heading(rider, 'Choose one instrument setup', y)
    y = para(rider, '<b>A / IR direct to PA - 3 instrument channels.</b> One mono DI / IR feed each from guitar left, guitar right and bass. No cabinet microphones and no additional bass channel in this mode.', y)
    y = para(rider, '<b>B / Amps and cabinets - 4 instrument channels.</b> One microphone per cabinet: guitar left, guitar right and bass. Bass also supplies one separate mono IR feed, giving two bass channels in total. No additional guitar DI / IR channels are required.', y)
    y = heading(rider, 'House PA, monitoring and power', y)
    y = para(rider, 'Please provide a suitable PA and FOH engineer, three vocal microphones with stands, and monitoring for the three front vocal positions, bass and drums. Provide mains power at both guitar rigs and the bass rig. Confirm monitor mixes and any shared feeds in advance.', y)
    assert y > 55, y
    rider.showPage()
    base(rider, 'INPUT LIST & VENUE ADVANCE | June 2027', 2, 2)
    y = para(rider, '<b>A / IR:</b> 12 active inputs (3 instruments + 3 vocals + 6 drums). <b>B / amps:</b> 13 active inputs (4 instruments + 3 vocals + 6 drums). Channel 4 is unused in IR mode; remaining channel numbers stay the same.', H - 120)
    rows = [['Ch', 'Source / position', 'A / IR direct to PA', 'B / Amps and cabinets'],
        ['1', 'Guitar - audience left', 'Mono DI / IR', 'One guitar cabinet mic'],
        ['2', 'Guitar - audience right', 'Mono DI / IR', 'One guitar cabinet mic'],
        ['3', 'Bass - back-left', 'Mono DI / IR', 'One bass cabinet mic'],
        ['4', 'Bass - additional feed', 'Not used', 'Mono DI / IR'],
        ['5', 'Lead vocal - center', 'Vocal mic + stand', 'Vocal mic + stand'],
        ['6', 'Backing vocal - guitar left', 'Vocal mic + boom', 'Vocal mic + boom'],
        ['7', 'Backing vocal - guitar right', 'Vocal mic + boom', 'Vocal mic + boom'],
        ['8', 'Kick drum', 'Kick dynamic mic', 'Kick dynamic mic'],
        ['9', 'Snare top', 'Dynamic mic', 'Dynamic mic'],
        ['10', 'Rack tom', 'Dynamic / clip mic', 'Dynamic / clip mic'],
        ['11', 'Floor tom', 'Dynamic / clip mic', 'Dynamic / clip mic'],
        ['12', 'Overhead - audience left', 'Condenser mic', 'Condenser mic'],
        ['13', 'Overhead - audience right', 'Condenser mic', 'Condenser mic']]
    table = Table([[Paragraph(str(cell), ParagraphStyle('cell', parent=P, fontSize=8.5, leading=11)) for cell in row] for row in rows], colWidths=[28, 167, 153, WIDTH - 348])
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), PAPER), ('LINEBELOW', (0,0), (-1,0), 1, INK), ('LINEBELOW', (0,1), (-1,-1), .4, GRAY), ('VALIGN',(0,0),(-1,-1),'TOP'), ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    _, th = table.wrap(WIDTH, H)
    table.drawOn(rider, M, y - th)
    y -= th + 18
    y = heading(rider, 'Basic drum microphone package', y)
    y = para(rider, 'Six microphones, with suitable stands or clips and cabling: kick, snare top, one rack tom, one floor tom and two overheads. Phantom power for overhead condensers as required by the microphones. This is the baseline mic plan; confirm the actual kit and any extra toms before the show.', y)
    y = heading(rider, 'Confirm before the show', y)
    y = para(rider, 'Agree IR or amp mode, cabinet and compatible amplifier supply, drum kit/backline supply, connector types and levels, DI boxes, monitor allocation, stage footprint, load-in, soundcheck and set length. In amp mode, keep cabinet simulation off conventional cabinet feeds and on the separate bass IR feed to FOH.', y)
    assert y > 55, y
    rider.save()
    print('Created technical rider (2 pages), stage plot (1 page), and SVG stage plot.')

if __name__ == '__main__':
    main()
