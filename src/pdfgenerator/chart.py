
from reportlab.lib.normalDate import NormalDate
from pdfgenerator.lineplots import LinePlot, LinePlotProperties
from reportlab.graphics.charts.legends import LineLegend
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String, Line
from reportlab.pdfbase.pdfmetrics import stringWidth, EmbeddedType1Face, registerTypeFace, Font, registerFont
from reportlab.lib.colors import PCMYKColor, black, white
from reportlab.graphics.charts.axes import XValueAxis, YValueAxis, AdjYValueAxis, NormalDateXValueAxis
from reportlab.lib.formatters import DecimalFormatter
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.validators import *
from reportlab.lib.attrmap import *


class dynamic_label(Label):
    def __init__(self,text,ux,uy,**kw):
        Label.__init__(self,**kw)
        self._text = text
        self._ux = ux
        self._uy = uy

    def as_annotation(self,chart,xscale,yscale):
        self.x = xscale(self._ux) #- 3 # moves it off the edge
        self.y = yscale(self._uy) #+ 7 # lift it up the chart
        return None

class covid_chart(LinePlot):
    """Line chart with multiple lines.
    Adapted from ReportLab LinePlot
    """

    _attrMap = AttrMap(BASE=LinePlot,  )

    def __init__(self):
        LinePlot.__init__(self)
        self.xValueAxis = NormalDateXValueAxis()

        # # Allow for a bounding rectangle.
        # self.strokeColor = None
        # self.fillColor = None
        #
        # # Named so we have less recoding for the horizontal one :-)
        # self.categoryAxis = XCategoryAxis()
        # self.valueAxis = YValueAxis()
        #
        # # This defines two series of 3 points.  Just an example.
        # self.data = [(100,110,120,130),
        #              (70, 80, 80, 90)]
        # self.categoryNames = ('North','South','East','West')
        #
        # self.lines = TypedPropertyCollection(LineChartProperties)
        # self.lines.strokeWidth = 1
        # self.lines[0].strokeColor = colors.red
        # self.lines[1].strokeColor = colors.green
        # self.lines[2].strokeColor = colors.blue
        #
        # # control spacing. if useAbsolute = 1 then
        # # the next parameters are in points; otherwise
        # # they are 'proportions' and are normalized to
        # # fit the available space.
        # self.useAbsolute = 0   #- not done yet
        # self.groupSpacing = 1 #5
        #
        # self.lineLabels = TypedPropertyCollection(Label)
        # self.lineLabelFormat = None
        # self.lineLabelArray = None
        #
        # # This says whether the origin is above or below
        # # the data point. +10 means put the origin ten points
        # # above the data point if value > 0, or ten
        # # points below if data value < 0.  This is different
        # # to label dx/dy which are not dependent on the
        # # sign of the data.
        # self.lineLabelNudge = 10
        # # If you have multiple series, by default they butt
        # # together.
        #
        # # New line chart attributes.
        # self.joinedLines = 1 # Connect items with straight lines.
        # self.inFill = 0
        # self.reversePlotOrder = 0
        #
        #
