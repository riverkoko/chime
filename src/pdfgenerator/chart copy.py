# simple_line_chart.py

from reportlab.lib import colors
from reportlab.lib.validators import isNumber, isNumberOrNone, isColor, isColorOrNone, isListOfStrings, \
                                    isListOfStringsOrNone, SequenceOf, isBoolean, NoneOr, \
                                    isListOfNumbersOrNone, isStringOrNone, OneOf, Percentage
from reportlab.lib.attrmap import *
from reportlab.lib.utils import flatten
from reportlab.graphics.widgetbase import Widget, TypedPropertyCollection, PropHolder, tpcGetItem
from reportlab.graphics.shapes import Line, Rect, Group, Drawing, Polygon, PolyLine
from reportlab.graphics.widgets.signsandsymbols import NoEntry
from reportlab.graphics.charts.axes import XCategoryAxis, YValueAxis
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.widgets.markers import uSymbol2Symbol, isSymbol, makeMarker
from reportlab.graphics.charts.areas import PlotArea
from reportlab.graphics.charts.legends import _objStr
from reportlab.graphics.charts.utils import FillPairedData

from reportlab.graphics.charts.linecharts import LineChart, LineChartProperties



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

class covid_chart(LineChart):
    """Line chart with multiple lines.

    Adapted from ReportLab HorizontalLineChart

    A line chart is assumed to have one category and one value axis.
    Despite its generic name this particular line chart class has
    a vertical value axis and a horizontal category one. It may
    evolve into individual horizontal and vertical variants (like
    with the existing bar charts).

    Available attributes are:

        x: x-position of lower-left chart origin
        y: y-position of lower-left chart origin
        width: chart width
        height: chart height

        useAbsolute: disables auto-scaling of chart elements (?)
        lineLabelNudge: distance of data labels to data points
        lineLabels: labels associated with data values
        lineLabelFormat: format string or callback function
        groupSpacing: space between categories

        joinedLines: enables drawing of lines

        strokeColor: color of chart lines (?)
        fillColor: color for chart background (?)
        lines: style list, used cyclically for data series

        valueAxis: value axis object
        categoryAxis: category axis object
        categoryNames: category names

        data: chart data, a list of data series of equal length
    """

    _attrMap = AttrMap(BASE=LineChart,
        useAbsolute = AttrMapValue(isNumber, desc='Flag to use absolute spacing values.',advancedUsage=1),
        lineLabelNudge = AttrMapValue(isNumber, desc='Distance between a data point and its label.',advancedUsage=1),
        lineLabels = AttrMapValue(None, desc='Handle to the list of data point labels.'),
        lineLabelFormat = AttrMapValue(None, desc='Formatting string or function used for data point labels.'),
        lineLabelArray = AttrMapValue(None, desc='explicit array of line label values, must match size of data if present.'),
        groupSpacing = AttrMapValue(isNumber, desc='? - Likely to disappear.'),
        joinedLines = AttrMapValue(isNumber, desc='Display data points joined with lines if true.'),
        lines = AttrMapValue(None, desc='Handle of the lines.'),
        valueAxis = AttrMapValue(None, desc='Handle of the value axis.'),
        categoryAxis = AttrMapValue(None, desc='Handle of the category axis.'),
        categoryNames = AttrMapValue(isListOfStringsOrNone, desc='List of category names.'),
        data = AttrMapValue(None, desc='Data to be plotted, list of (lists of) numbers.'),
        inFill = AttrMapValue(isBoolean, desc='Whether infilling should be done.',advancedUsage=1),
        reversePlotOrder = AttrMapValue(isBoolean, desc='If true reverse plot order.',advancedUsage=1),
        annotations = AttrMapValue(None, desc='list of callables, will be called with self, xscale, yscale.',advancedUsage=1),
        )

    def __init__(self):
        LineChart.__init__(self)

        # Allow for a bounding rectangle.
        self.strokeColor = None
        self.fillColor = None

        # Named so we have less recoding for the horizontal one :-)
        self.categoryAxis = XCategoryAxis()
        self.valueAxis = YValueAxis()

        # This defines two series of 3 points.  Just an example.
        self.data = [(100,110,120,130),
                     (70, 80, 80, 90)]
        self.categoryNames = ('North','South','East','West')

        self.lines = TypedPropertyCollection(LineChartProperties)
        self.lines.strokeWidth = 1
        self.lines[0].strokeColor = colors.red
        self.lines[1].strokeColor = colors.green
        self.lines[2].strokeColor = colors.blue

        # control spacing. if useAbsolute = 1 then
        # the next parameters are in points; otherwise
        # they are 'proportions' and are normalized to
        # fit the available space.
        self.useAbsolute = 0   #- not done yet
        self.groupSpacing = 1 #5

        self.lineLabels = TypedPropertyCollection(Label)
        self.lineLabelFormat = None
        self.lineLabelArray = None

        # This says whether the origin is above or below
        # the data point. +10 means put the origin ten points
        # above the data point if value > 0, or ten
        # points below if data value < 0.  This is different
        # to label dx/dy which are not dependent on the
        # sign of the data.
        self.lineLabelNudge = 10
        # If you have multiple series, by default they butt
        # together.

        # New line chart attributes.
        self.joinedLines = 1 # Connect items with straight lines.
        self.inFill = 0
        self.reversePlotOrder = 0


    def demo(self):
        """Shows basic use of a line chart."""

        drawing = Drawing(200, 100)

        data = [
                (13, 5, 20, 22, 37, 45, 19, 4),
                (14, 10, 21, 28, 38, 46, 25, 5)
                ]

        lc = HorizontalLineChart()

        lc.x = 20
        lc.y = 10
        lc.height = 85
        lc.width = 170
        lc.data = data
        lc.lines.symbol = makeMarker('Circle')

        drawing.add(lc)

        return drawing

    def calcPositions(self):
        """Works out where they go.

        Sets an attribute _positions which is a list of
        lists of (x, y) matching the data.
        """

        self._seriesCount = len(self.data)
        self._rowLength = max(list(map(len,self.data)))

        if self.useAbsolute:
            # Dimensions are absolute.
            normFactor = 1.0
        else:
            # Dimensions are normalized to fit.
            normWidth = self.groupSpacing
            availWidth = self.categoryAxis.scale(0)[1]
            normFactor = availWidth / normWidth
        self._normFactor = normFactor
        self._yzero = yzero = self.valueAxis.scale(0)
        self._hngs = hngs = 0.5 * self.groupSpacing * normFactor

        pairs = set()
        P = [].append
        cscale = self.categoryAxis.scale
        vscale = self.valueAxis.scale
        data = self.data
        n = len(data)
        for rowNo,row in enumerate(data):
            if isinstance(row, FillPairedData):
                other = row.other
                if 0<=other<n:
                    if other==rowNo:
                        raise ValueError('data row %r may not be paired with itself' % rowNo)
                    t = (rowNo,other)
                    pairs.add((min(t),max(t)))
                else:
                    raise ValueError('data row %r is paired with invalid data row %r' % (rowNo, other))
            line = [].append
            for colNo,datum in enumerate(row):
                if datum is not None:
                    groupX, groupWidth = cscale(colNo)
                    x = groupX + hngs
                    y = yzero
                    height = vscale(datum) - y
                    line((x, y+height))
            P(line.__self__)
        P = P.__self__

        #if there are some paired lines we ensure only one is created
        for rowNo, other in pairs:
            P[rowNo] = FillPairedData(P[rowNo],other)
        self._pairInFills = len(pairs)
        self._positions = P


    def getPositions(self):
        return self._positions

    def _innerDrawLabel(self, rowNo, colNo, x, y):
        "Draw a label for a given item in the list."
        # print( rowNo, colNo, x, y, self.lineLabelArray[rowNo][colNo])

        labelFmt = self.lineLabelFormat
        labelValue = self.data[rowNo][colNo]

        if labelFmt is None:
            labelText = None
        elif type(labelFmt) is str:
            if labelFmt == 'values':
                try:
                    labelText = self.lineLabelArray[rowNo][colNo]
                except:
                    labelText = None
            else:
                labelText = labelFmt % labelValue
        elif hasattr(labelFmt,'__call__'):
            labelText = labelFmt(labelValue)
        else:
            raise ValueError("Unknown formatter type %s, expected string or function"%labelFmt)

        if labelText:
            label = self.lineLabels[(rowNo, colNo)]
            if not label.visible: return
            # Make sure labels are some distance off the data point.
            if y > 0:
                label.setOrigin(x, y + self.lineLabelNudge)
            else:
                label.setOrigin(x, y - self.lineLabelNudge)
            label.setText(labelText)
        else:
            label = None
        return label

    def drawLabel(self, G, rowNo, colNo, x, y):
        '''Draw a label for a given item in the list.
        G must have an add method'''
        G.add(self._innerDrawLabel(rowNo,colNo,x,y))

    def makeLines(self):
        g = Group()

        labelFmt = self.lineLabelFormat
        P = self._positions
        if self.reversePlotOrder: P.reverse()
        lines = self.lines
        styleCount = len(lines)
        _inFill = self.inFill
        if (_inFill or self._pairInFills or
                [rowNo for rowNo in range(len(P))
                        if getattr(lines[rowNo%styleCount],'inFill',False)]
                ):
            inFillY = self.categoryAxis._y
            inFillX0 = self.valueAxis._x
            inFillX1 = inFillX0 + self.categoryAxis._length
            inFillG = getattr(self,'_inFillG',g)
        yzero = self._yzero

        # Iterate over data rows.
        for rowNo, row in enumerate(reversed(P) if self.reversePlotOrder else P):
            styleIdx = rowNo % styleCount
            rowStyle = lines[styleIdx]
            strokeColor = rowStyle.strokeColor
            fillColor = getattr(rowStyle,'fillColor',strokeColor)
            inFill = getattr(rowStyle,'inFill',_inFill)
            dash = getattr(rowStyle, 'strokeDashArray', None)
            lineStyle = getattr(rowStyle,'lineStyle',None)

            if hasattr(rowStyle, 'strokeWidth'):
                strokeWidth = rowStyle.strokeWidth
            elif hasattr(lines, 'strokeWidth'):
                strokeWidth = lines.strokeWidth
            else:
                strokeWidth = None

            # Iterate over data columns.
            if lineStyle=='bar':
                barWidth = getattr(rowStyle,'barWidth',Percentage(50))
                if isinstance(barWidth,Percentage):
                    hbw = self._hngs*barWidth*0.01
                else:
                    hbw = barWidth*0.5
                for x, y in row:
                    g.add(Rect(x-hbw,min(y,yzero),2*hbw,abs(y-yzero),strokeWidth=strokeWidth,strokeColor=strokeColor,fillColor=fillColor))
            elif self.joinedLines or lineStyle=='joinedLine':
                points = flatten(row)
                if inFill or isinstance(row,FillPairedData):
                    filler = getattr(rowStyle, 'filler', None)
                    if isinstance(row,FillPairedData):
                        fpoints = points + flatten(reversed(P[row.other]))
                    else:
                        fpoints = [inFillX0,inFillY] + points + [inFillX1,inFillY]
                    if filler:
                        filler.fill(self,inFillG,rowNo,fillColor,fpoints)
                    else:
                        inFillG.add(Polygon(fpoints,fillColor=fillColor,strokeColor=strokeColor if strokeColor==fillColor else None,strokeWidth=strokeWidth or 0.1))
                if not inFill or inFill==2 or strokeColor!=fillColor:
                    line = PolyLine(points,strokeColor=strokeColor,strokeLineCap=0,strokeLineJoin=1)
                    if strokeWidth:
                        line.strokeWidth = strokeWidth
                    if dash:
                        line.strokeDashArray = dash
                    g.add(line)

            if hasattr(rowStyle, 'symbol'):
                uSymbol = rowStyle.symbol
            elif hasattr(lines, 'symbol'):
                uSymbol = lines.symbol
            else:
                uSymbol = None

            if uSymbol:
                for colNo,(x,y) in enumerate(row):
                    symbol = uSymbol2Symbol(tpcGetItem(uSymbol,colNo),x,y,rowStyle.strokeColor)
                    if symbol: g.add(symbol)

            # Draw item labels.
            for colNo, (x, y) in enumerate(row):
                self.drawLabel(g, rowNo, colNo, x, y)

        return g

    def draw(self):
        "Draws itself."

        vA, cA = self.valueAxis, self.categoryAxis
        vA.setPosition(self.x, self.y, self.height)
        if vA: vA.joinAxis = cA
        if cA: cA.joinAxis = vA
        vA.configure(self.data)

        # If zero is in chart, put x axis there, otherwise
        # use bottom.
        xAxisCrossesAt = vA.scale(0)
        if ((xAxisCrossesAt > self.y + self.height) or (xAxisCrossesAt < self.y)):
            y = self.y
        else:
            y = xAxisCrossesAt

        cA.setPosition(self.x, y, self.width)
        cA.configure(self.data)

        self.calcPositions()

        g = Group()
        g.add(self.makeBackground())
        if self.inFill:
            self._inFillG = Group()
            g.add(self._inFillG)

        g.add(cA)
        g.add(vA)
        cAdgl = getattr(cA,'drawGridLast',False)
        vAdgl = getattr(vA,'drawGridLast',False)
        if not cAdgl: cA.makeGrid(g,parent=self,dim=vA.getGridDims)
        if not vAdgl: vA.makeGrid(g,parent=self,dim=cA.getGridDims)
        g.add(self.makeLines())
        if cAdgl: cA.makeGrid(g,parent=self,dim=vA.getGridDims)
        if vAdgl: vA.makeGrid(g,parent=self,dim=cA.getGridDims)
        for a in getattr(self,'annotations',()): g.add(a(self,cA.scale,vA.scale))
        return g
