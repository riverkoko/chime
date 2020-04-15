# header3.py
from datetime import datetime
from datetime import date
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import inch
import os
from penn_chime.constants import VERSION

def header(canvas, doc):
    width, height = doc.pagesize

    canvas.saveState()

    current_scenario_title = doc.scenario_parameters['Location Code'][doc.current_scenario]

    has_logo = os.path.exists( doc.logo_path + current_scenario_title + '.png' )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))

    rg = datetime.strftime(datetime.strptime( doc.scenario_parameters['Report Generated'][doc.current_scenario], '%m/%d/%Y %H:%M:%S'), '%d %b %Y')

    actuals_date = doc.scenario_parameters['Actuals as of'][doc.current_scenario]
    actuals_date = datetime.strptime(actuals_date, '%m/%d/%Y')
    if actuals_date.year == 1980:
        actuals_date = "-"
    else:
        actuals_date = datetime.strftime(actuals_date, '%d %b %Y')

    ptext = '''<font size=8 name="Calibri">Actuals as of: </font><br />
        <font size=8 name="Calibri">CHIME Projections Report Date: </font>
        '''

    p = Paragraph(ptext, styles["RightAlign"])
    p.wrapOn(canvas, width, height)
    if has_logo:
        p.drawOn(canvas, -1.7*inch, 16.32*inch)
    else:
        p.drawOn(canvas, -1.2*inch, 16.32*inch)

    ptext = '''<font size=8 color="Red"><b>{actuals}</b></font><br />
        <font size=8 color="Red"><b>{chime}</b></font>
        '''.format(actuals=actuals_date, chime=rg)

    p = Paragraph(ptext, styles["RightAlign"])
    p.wrapOn(canvas, width, height)
    if has_logo:
        p.drawOn(canvas, -inch, 16.32*inch)
    else:
        p.drawOn(canvas, -0.5*inch, 16.32*inch)

    img = Image(doc.logo_path + doc.logo, width=0.5*inch, height=0.5*inch)
    img.wrapOn(canvas, width, height)
    img.drawOn(canvas, 0.25*inch, 16.25*inch)

    if has_logo:
        img = Image(doc.logo_path + current_scenario_title + '.png', width=0.5*inch, height=0.5*inch)
        img.wrapOn(canvas, width, height)
        img.drawOn(canvas, 10.25*inch, 16.25*inch)

    canvas.setLineWidth(0.25)
    # canvas.line(0.25*inch, 16.75*inch, 10.75*inch, 16.75*inch)
    # canvas.line(0.25*inch, 16.50*inch, 10.75*inch, 16.50*inch)
    # canvas.line(0.25*inch, 16.25*inch, 10.75*inch, 16.25*inch)
    canvas.line(0.25*inch, 0.75*inch, 10.75*inch, 0.75*inch)

    # p.drawOn(canvas, 0, 0)

    canvas.setLineWidth(0.5)
    # canvas.setStrokeColor("blue")

    canvas.line(0.25*inch, 16*inch, 10.75*inch, 16*inch)

    ptext = '<font size=9>UPenn COVID-19 Hospital Impact Model for Epidemics (C.H.I.M.E.) {version}</font>'.format(version=VERSION)
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, inch, 16.56*inch)

    ptext = '<font size=6 color="#aaaaaa">Model source and additional information available at <a color="blue" href="https://penn-chime.phl.io/">https://penn-chime.phl.io/</a></font>'
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, 0.3*inch, 0.45*inch)

    ptext = '<font size=10><b>Projected Daily Inpatient Load (Census)</b></font>'
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, 1*inch, 16.41*inch)

    ptext = '<font size=6 color="#555555"><i>Projected census of COVID-19 inpatients, accounting for arrivals and discharges</i></font>'
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, 1*inch, 16.22*inch)

    ptext = '<font size=10><b>' + current_scenario_title + '</b></font>'
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, inch, 16.0*inch)

    canvas.restoreState()


def cover_header(canvas, doc) :

    width, height = doc.pagesize
    canvas.saveState()

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))

    ptext = '<font size=8 name="Calibri">Report Date: </font><font size=8 color="Red"><b>{chime}</b></font>'.format(chime='01/02/2017')
    p = Paragraph(ptext, styles["Normal"]) #RightAlign"])
    p.wrapOn(canvas, width, height)
    # p.drawOn(canvas, -inch, 16.25*inch)
    # p.drawOn(canvas, 2*inch, 17.75*inch)

    img = Image(doc.logo_path + doc.logo, width=0.5*inch, height=0.5*inch)
    img.wrapOn(canvas, width, height)
    img.drawOn(canvas, 0.25*inch, 16.25*inch)

    current_scenario_title = doc.scenario_parameters['Location Code'][doc.current_scenario]

    has_logo = os.path.exists( doc.logo_path + current_scenario_title + '.png' )

    if has_logo:
        img = Image(doc.logo_path + current_scenario_title + '.png', width=0.5*inch, height=0.5*inch)
        img.wrapOn(canvas, width, height)
        img.drawOn(canvas, 10.25*inch, 16.25*inch)

    ptext = '<font size=18 name="CalibriBd">COVID19 Hospitalization Projections</font>'
    p = Paragraph(ptext, styles["Normal"])
    p.wrapOn(canvas, width, height)
    p.drawOn(canvas, 1*inch, 16.5*inch)

    canvas.restoreState()
