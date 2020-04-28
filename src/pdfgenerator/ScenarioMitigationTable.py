# boxy_line.py
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line

from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import HexColor

def format_parameter(pv, percent=False):

    t = str(type(pv))
    v = "Not Supported"

    if 'int' in t:
        v = "{:,.0f}".format(pv)
    elif 'float' in t:
        if percent:
            v= "{:,.2f}%".format(pv*100)
        else :
            v = "{:,.2f}".format(pv)
    elif 'str' in t:
        v = pv
    elif 'datetime' in t:
        v = pv.strftime("%d-%b")
    elif 'NoneType' in t:
        v = "None"

    return v

class ScenarioMitigationTable():

    def __init__(self
        , mitigations=None
        ):
        Flowable.__init__(self)
        self.mitigations=mitigations

    def getTable(self):
        data = [
            ['Mitigation', 'Date', 'Social Distancing Impact', 'Rt', 'Effective Doubling Time', 'Daily Growth Rate', ],
        ]

        self.mitigations.reset_index(drop=True, inplace=True)

        for index, row in self.mitigations.iterrows():
            data.append( [
                "{:,}. {}".format(index + 1, row["notes"]),
                format_parameter(row["mitigation_date"]),
                format_parameter(row["sd"], percent=True),
                format_parameter(row["r_t"]),
                "{} days".format(format_parameter(row["doubling_time_t"])),
                format_parameter(row["daily_growth_rate_t"], percent=True),
                ])

        t = Table(data)

        t.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,0), 0.5, HexColor("#a2b7e0")),

            ('LINEBELOW', (0,1), (-1,-1), 0.25, HexColor("#dddddd")),

            ('FONT', (0,0), (-1,0), "CalibriBd", 6 ),
            ('FONT', (0,1), (-1,-1), "Calibri", 5 ),

            ('ALIGN', (1,0), (-1,-1), "CENTER"),
            ('ALIGN', (0,0), (0,-1), "LEFT"),

        ]))

        return t
