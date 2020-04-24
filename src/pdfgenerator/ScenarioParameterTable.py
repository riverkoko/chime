# boxy_line.py
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line

from reportlab.pdfbase.pdfmetrics import stringWidth


class ScenarioParameterTable(Flowable):

    def __init__(self
        , x=0
        , y=-15
        , width=40
        , params=None
        ):
        Flowable.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = inch
        self.styles = getSampleStyleSheet()
        self.params=params

    def coord(self, x, y, unit=1):
        """
        http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
        Helper class to help position flowables in Canvas objects
        """
        x, y = x * unit, self.height -  y * unit
        return x,y

    def hlinecoord(self, x, y, len, unit=1):
        x, y = x * unit, self.height -  y * unit
        x1, y1 = x + (len * unit) , y
        return x, y, x1, y1

    def vlinecoord(self, x, y, len, unit=1):
        x, y = x * unit, self.height -  y * unit
        x1, y1 = x, y - (len * unit)
        return x, y, x1, y1

    def draw(self):
        """
        Draw the shape, text, etc
        """
        w, h = self.canv._pagesize
        self.canv.saveState()



        self.canv.restoreState()

#162, 183, 224
