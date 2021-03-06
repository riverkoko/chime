import datetime

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.platypus import Flowable, Paragraph
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line, Polygon
from pdfgenerator.chart import covid_chart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.validators import Auto
from reportlab.lib.normalDate import NormalDate


class DynamicDrawing(Drawing):
    def __init__(self, width=400, height=200, *nodes, **keywords):
        Drawing.__init__(self, width, height, *nodes, **keywords)

    def getContents(self):

        return Drawing.getContents(self)

class ScenarioGraph(Flowable):

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
        self.height = 4.1*inch
        self.styles = getSampleStyleSheet()
        self.params=params

    def label_formatter(self, graph, rowNo, colNo, x, y):
        lbl = ''
        lbls = ['MedSurg', 'ICU', 'Ventilated', 'MedSurg', 'ICU', 'Ventilated', 'MedSurg', 'ICU', 'Ventilated', ]
        voffset = 0
        if rowNo < 9:
            cdate = str(graph.data[rowNo][colNo][0])
            d1 = self.params["peaks"][rowNo][0][0]

            if d1 == cdate and cdate != str(graph.data[rowNo][-1][0]) and self.params["peaks"][rowNo][0][1] >= 1.0:
                d = datetime.datetime.strptime(self.params["peaks"][rowNo][0][0], "%Y%m%d")
                lbl = "{} Peak: {:,.0f} on {}".format(lbls[rowNo],self.params["peaks"][rowNo][0][1], d.strftime("%d-%b"))

            if lbls[rowNo] == 'ICU':
                voffset = 8

        return (lbl, voffset)

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

        d = DynamicDrawing(width=self.width, height=self.height)
        d2 = DynamicDrawing(width=self.width, height=self.height)

        self.styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='CenterAlign', alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_header'
            , fontName = 'CalibriBd'
            , fontSize = 5
            , leading = 6
            , textColor = "#43536a"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_init'
            , fontName = 'CalibriBd'
            , fontSize = 8
            , textColor = "#c00101"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='today'
            , fontName = 'CalibriBd'
            , fontSize = 6
            , textColor = "#c00101"
            , alignment=TA_LEFT))

        self.styles.add(ParagraphStyle(name='box_init_value'
            , fontName = 'CalibriBd'
            , fontSize = 12
            , textColor = "#c00101"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_result_title'
            , fontName = 'Calibri'
            , fontSize = 4
            , textColor = "#000000"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_result'
            , fontName = 'Calibri'
            , fontSize = 6
            , textColor = "#000000"
            , alignment=TA_CENTER))

        self.canv.saveState()

        line = covid_chart()
        line.x = inch*0.1
        line.y = 0.5 * inch
        line.height = 3.8*inch
        line.width = 8*inch

        # line.data = self.params

        line.data = [
            self.params["hosp-sd-norm"] ,
            self.params["icu-sd-norm"],
            self.params["vent-sd-norm"],
            self.params["hosp-sd-0"],
            self.params["icu-sd-0"],
            self.params["vent-sd-0"],
            self.params["hosp-sd-1"],
            self.params["icu-sd-1"],
            self.params["vent-sd-1"],
         ]

        series = (
            'MedSurg ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][0][0]*100),
            'ICU ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][0][0]*100),
            'Ventilated ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][0][0]*100),

            'MedSurg ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][1][0]*100),
            'ICU ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][1][0]*100),
            'Ventilated ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][1][0]*100),

            'MedSurg ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][2][0]*100),
            'ICU ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][2][0]*100),
            'Ventilated ({sd:.0f}% reduction in social contact)'.format(sd=self.params["sd"][2][0]*100),
            )
        for i, s in enumerate(series): line.lines[i].name = s

        lbldates = []
        for dt in self.params["labeled-dates"]:
            lbldates.append(dt[0])

        line.xValueAxis.strokeWidth = 0.25
        line.xValueAxis.strokeColor = HexColor("#dddddddd", hasAlpha=True)
        line.xValueAxis.tickDown = 1 * mm
        line.xValueAxis.labels.fontName = "Calibri"
        line.xValueAxis.labels.fontSize = 5
        line.xValueAxis.labels.angle = -90
        line.xValueAxis.labels.dx = 3.3
        line.xValueAxis.labels.dy = -10.0

        line.xValueAxis.gridStrokeWidth = 0.25
        line.xValueAxis.gridStrokeColor = HexColor("#dddddddd", hasAlpha=True)
        line.xValueAxis.visibleGrid = 1
        line.xValueAxis.xLabelFormat = "{dd}-{mmm}"
        line.xValueAxis.forceFirstDate = line.xValueAxis.forceEndDate = True
        line.xValueAxis.niceMonth = True
        line.xValueAxis.specifiedTickDates = lbldates

        line.yValueAxis.strokeWidth = 0.25
        line.yValueAxis.strokeColor = HexColor("#dddddd")
        line.yValueAxis.labels.fontName = "Calibri"
        line.yValueAxis.labels.fontSize = 6
        line.yValueAxis.labelTextFormat = "{:,.0f}"

        ymax = ((self.params["ymax"] + 10) // 10) * 10

        line.yValueAxis.valueMin = 0
        line.yValueAxis.valueMax = ymax
        line.yValueAxis.valueStep = ymax // 10
        # line.yValueAxis.dumpProperties()

        line.lineLabelFormat = self.label_formatter
        line.lineLabels.fontName = "Calibri"
        line.lineLabels.fontSize = 5
        line.lineLabelNudge = 0.05 * inch

        line_colors = [
                        [ HexColor("#5c9bd5aa", hasAlpha=True), HexColor("#ffbf01aa", hasAlpha=True), HexColor("#c00101aa", hasAlpha=True) ],
                        [ HexColor("#5c9bd5ff", hasAlpha=True), HexColor("#ffbf01ff", hasAlpha=True), HexColor("#c00101ff", hasAlpha=True) ],
                        [ HexColor("#5c9bd588", hasAlpha=True), HexColor("#ffbf0188", hasAlpha=True), HexColor("#c0010188", hasAlpha=True) ],
                      ]
        line_widths = [ 0.75, 1.5, 0.5 ]

        for li in range(3):
            for li2 in range(3):
                line.lines[li*3 + li2].strokeColor = line_colors[li][li2]
                line.lines[li*3 + li2].strokeWidth = line_widths[li]

        for li in range(0,3):
            line.lines[li].strokeDashArray = ( 2, 2 )

        for li in range(6,9):
            line.lines[li].strokeDashArray = ( 1, 3 )

        if self.params["hosp-beds"][0][1] > 0:
            lc = len(line.data)
            line.data.append( self.params["hosp-beds"] )
            line.lines[lc].strokeDashArray = ( 1, 1 )
            line.lines[lc].strokeWidth = 0.5
            line.lines[lc].strokeColor = HexColor("#335aa2")
            line.lines[lc].name = "MedSurg Bed Capacity"

        if self.params["icu-beds"][0][1] > 0:
            lc = len(line.data)
            line.data.append( self.params["icu-beds"] )
            line.lines[lc].strokeDashArray = ( 1, 1 )
            line.lines[lc].strokeWidth = 0.5
            line.lines[lc].strokeColor = HexColor("#ffbf01")
            line.lines[lc].name = "ICU Bed Capacity"

        if self.params["vent-beds"][0][1] > 0:
            lc = len(line.data)
            line.data.append( self.params["vent-beds"] )
            line.lines[lc].strokeDashArray = ( 1, 1 )
            line.lines[lc].strokeWidth = 0.5
            line.lines[lc].strokeColor = HexColor("#c00101")
            line.lines[lc].name = "Ventilated Bed Capacity"

        legend = Legend()

        legend.alignment = 'right'
        legend.x = 8.25*inch
        legend.y = 2.0*inch
        legend.colorNamePairs = Auto(obj=line)
        legend.columnMaximum = 12
        legend.fontName = "Calibri"
        legend.fontSize = 5
        legend.deltay = 1

        d.add(line, 'graph')

        d.add(legend)

        leftm = (2.67 * 3 - 1) # aligning with the header
        gap = 0.06
        vp  = 0.25
        col = (3 / 5)

        has_medsurg = (self.params['beds'][0] > 0)
        has_icu     = (self.params['beds'][1] > 0)
        has_vent    = (self.params['beds'][2] > 0)

        ladj = 0
        if not has_medsurg: ladj += col
        if not has_icu: ladj += col
        if not has_vent: ladj += col

        d.add(Rect(*self.coord(leftm, 0.5-vp, inch), 3 * inch, 0.5*inch, strokeColor="#ffffff", fillColor="#ffffff", strokeWidth=1.0 ))

        d.add(Rect(*self.coord(leftm, vp, inch), 3 * inch, 0.25*inch, strokeColor="#7e7f7f", fillColor="#eeeeee", strokeWidth=0.25 ))
        d.add(Line(*self.vlinecoord( leftm + 1, vp - 0.25, 0.25, inch), strokeColor="#7e7f7f", strokeWidth=0.25 ))
        d.add(Line(*self.vlinecoord( leftm + 2, vp - 0.25, 0.25, inch), strokeColor="#7e7f7f", strokeWidth=0.25 ))
        d.add(Line(*self.hlinecoord(leftm, 0, 3, inch), strokeColor="#a2b7e0", strokeWidth=0.5 ))

        vp += 0.25
        d.add(Rect(*self.coord(leftm + ladj, vp, inch), (3 - ladj) * inch, 0.25*inch - 2, strokeColor="#ffffff", fillColor="#ffffff", strokeWidth=0.1 ))
        d.add(Rect(*self.coord(leftm + ladj, vp + 0.75, inch), (3 - ladj) * inch, 0.75*inch, strokeColor="#7e7f7f", fillColor="#eeeeee", strokeWidth=0.25 ))
        for r in range(2):
            d.add(Line(*self.hlinecoord(leftm + ladj, (vp + 0.25) + r*0.25, (3 - ladj), inch), strokeColor="#7e7f7f", strokeWidth=0.25 ))

        cc = 1
        for include in ( True, has_medsurg, has_icu, has_vent ):
            if include:
                d.add(Line(*self.vlinecoord( leftm + ladj + cc * col, vp, 0.75, inch), strokeColor="#7e7f7f", strokeWidth=0.25 ))
                cc += 1

        d.add(Line(*self.hlinecoord(leftm + ladj, vp, (3 - ladj), inch), strokeColor="#a2b7e0", strokeWidth=0.5 ))

        self.canv.restoreState()

        d.drawOn( self.canv, 0, 0)

        vp  = 0.25

        self.canv.saveState()

        self.canv.setStrokeColor("#c00101")
        self.canv.setLineWidth(0.25)

        day_zero = line.get_day_x(0)
        self.canv.line(day_zero[0], day_zero[1], day_zero[0], day_zero[2]  )

        p = Paragraph("Today", style=self.styles["today"])
        p.wrapOn(self.canv, 0.75*inch, self.height*2)
        p.drawOn(self.canv, day_zero[0] - 0.1*inch, day_zero[2])

        self.canv.setFillColor("#c00101")
        p = Polygon(points=[
            day_zero[0] + 0.03*inch, day_zero[2] + 0.05*inch,
            day_zero[0] - 0.03*inch, day_zero[2] + 0.05*inch,
            day_zero[0], day_zero[2] - 0.25,
            ])
        p.fillColor = HexColor("#c00101")
        p.strokeColor = HexColor("#ffffff")
        p.strokeWidth = 0.01

        d2.add(p)
        d2.drawOn(self.canv, 0, 0)

        #
        # add table for hospitalized patients
        #
        for hdr, pos in (('Currently Hospitalized COVID-19 Patients', leftm),
            ('Inpatient Precautionary Patients', leftm + 1 ),
            ('Inpatient Positive', leftm + 2 ),
            ) :
            p = Paragraph(hdr, style=self.styles["box_header"])
            p.wrapOn(self.canv, 0.75*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(pos + 0.125, vp - 0.28, inch))

        vp += 0.25
        for hdr, pos in (("{:,.0f}".format(self.params['current-inpatient'][0] + self.params['current-inpatient'][1]), leftm ),
            ("{:,.0f}".format(self.params['current-inpatient'][1]), leftm + 1 ),
            ("{:,.0f}".format(self.params['current-inpatient'][0]), leftm + 2 ),
            ) :
            p = Paragraph(hdr, style=self.styles["box_init"])
            p.wrapOn(self.canv, 0.75*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(pos + 0.125, vp - 0.28, inch))


        # Social contact reduction table with days to peak / days to capacity
        vp = 0.75
        cc = 0
        for hdr, include in (
            ("Social Contact Reduction", True ),
            ("Days to Peak", True ),
            ("Days to MedSurg Capacity", has_medsurg ),
            ("Days to ICU Capacity", has_icu ),
            ("Days to Ventilator Capacity", has_vent ),
            ) :
            if include:
                pos = leftm + ladj + (col * cc) + ( 0.05 * col )
                p = Paragraph(hdr, style=self.styles["box_header"])
                p.wrapOn(self.canv, col*inch*.9, self.height*2)
                p.drawOn(self.canv, *self.coord(pos, vp - 0.28, inch))
                cc += 1


        vp = 0.75
        for hdr, pos in (
            ("{:,.0f}%".format(self.params['sd'][0][0]*100), 0 ),
            ("{:,.0f}%".format(self.params['sd'][1][0]*100), 0.25 ),
            ("{:,.0f}%".format(self.params['sd'][2][0]*100), 0.5 ),
            ) :
            p = Paragraph(hdr, style=self.styles["box_result"])
            p.wrapOn(self.canv, col*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(leftm + ladj, pos + vp - 0.007, inch))

        pk = [
            self.params['sd'][0][1],
            self.params['sd'][1][1],
            self.params['sd'][2][1],
            ]

        pks = []
        for p in range(3):
            if self.params['sd'][p][1] is None:
                pks.append("-")
            else:
                pks.append("{:,.0f}".format(self.params['sd'][p][1]))

        for hdr, pos in (
            (pks[0], 0    ),
            (pks[1], 0.25 ),
            (pks[2], 0.5  ),
            ) :
            p = Paragraph(hdr, style=self.styles["box_result"])
            p.wrapOn(self.canv, col*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(leftm + ladj + col, pos + vp - 0.007, inch))

        cc = 0
        if has_medsurg :
            caps = []
            for p in (0, 3, 6):
                if self.params['capacity'][p] is None:
                    caps.append("-")
                else:
                    caps.append("{:,.0f} ({})".format(self.params['capacity'][p][1], NormalDate(self.params['capacity'][p][0]).formatMS('{DD}-{MMM}')))

            for hdr, pos in (
                (caps[0], 0    ),
                (caps[1], 0.25 ),
                (caps[2], 0.5  ),
                ) :
                p = Paragraph(hdr, style=self.styles["box_result"])
                p.wrapOn(self.canv, col*inch, self.height*2)
                p.drawOn(self.canv, *self.coord(leftm + ladj + col*(cc+2), pos + vp - 0.007, inch))
            cc += 1

        if has_icu :
            caps = []
            for p in (1, 4, 7):
                if self.params['capacity'][p] is None:
                    caps.append("-")
                else:
                    caps.append("{:,.0f} ({})".format(self.params['capacity'][p][1], NormalDate(self.params['capacity'][p][0]).formatMS('{DD}-{MMM}')))

            for hdr, pos in (
                (caps[0], 0    ),
                (caps[1], 0.25 ),
                (caps[2], 0.5  ),
                ) :
                p = Paragraph(hdr, style=self.styles["box_result"])
                p.wrapOn(self.canv, col*inch, self.height*2)
                p.drawOn(self.canv, *self.coord(leftm + ladj + (col * (2+cc)), pos + vp - 0.007, inch))
            cc += 1

        if has_vent :
            caps = []
            for p in (2, 5, 8):
                if self.params['capacity'][p] is None:
                    caps.append("-")
                else:
                    caps.append("{:,.0f} ({})".format(self.params['capacity'][p][1], NormalDate(self.params['capacity'][p][0]).formatMS('{DD}-{MMM}')))

            for hdr, pos in (
                (caps[0], 0    ),
                (caps[1], 0.25 ),
                (caps[2], 0.5  ),
                ) :
                p = Paragraph(hdr, style=self.styles["box_result"])
                p.wrapOn(self.canv, col*inch, self.height*2)
                p.drawOn(self.canv, *self.coord(leftm + ladj + (col * (2+cc)), pos + vp - 0.007, inch))
            cc += 1

# d = datetime.datetime.strptime(self.params["peaks"][rowNo][0][0], "%Y%m%d")
# lbl = "{:,.0f} on {}".format(self.params["peaks"][rowNo][0][1], d.strftime("%d-%b"))

        self.canv.translate(inch,inch)
        self.canv.rotate(90)
        p = Paragraph("Daily Inpatient Load (Projected Census)", style=self.styles["box_header"])
        p.wrapOn(self.canv, 2*inch, self.height*2)
        p.drawOn(self.canv, *self.coord( 0.75, 2.9, inch))



        self.canv.restoreState()


class ScenarioInflectedGraph(Flowable):

    def __init__(self
        , x=0
        , y=0
        , width=40
        , params=None
        , sir=False
        ):
        Flowable.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = 4.125*inch
        self.styles = getSampleStyleSheet()
        self.params=params
        self.sir = sir

    def label_formatter(self, graph, rowNo, colNo, x, y):
        lbl = ''
        lbls = ['MedSurg', 'ICU', 'Ventilated', 'MedSurg', 'ICU', 'Ventilated', 'MedSurg', 'ICU', 'Ventilated', ]
        voffset = 0
        # if rowNo < 9:
        #     cdate = str(graph.data[rowNo][colNo][0])
        #     d1 = self.params["peaks"][rowNo][0][0]
        #
        #     if d1 == cdate and cdate != str(graph.data[rowNo][-1][0]) and self.params["peaks"][rowNo][0][1] >= 1.0:
        #         d = datetime.datetime.strptime(self.params["peaks"][rowNo][0][0], "%Y%m%d")
        #         lbl = "{} Peak: {:,.0f} on {}".format(lbls[rowNo],self.params["peaks"][rowNo][0][1], d.strftime("%d-%b"))
        #
        #     if lbls[rowNo] == 'ICU':
        #         voffset = 8

        return (lbl, voffset)

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

        d = DynamicDrawing(width=self.width, height=self.height)
        d2 = DynamicDrawing(width=self.width, height=self.height)

        self.styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='CenterAlign', alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_header'
            , fontName = 'CalibriBd'
            , fontSize = 5
            , leading = 6
            , textColor = "#43536a"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_init'
            , fontName = 'CalibriBd'
            , fontSize = 8
            , textColor = "#c00101"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='today'
            , fontName = 'CalibriBd'
            , fontSize = 6
            , textColor = "#c00101"
            , alignment=TA_LEFT))

        self.styles.add(ParagraphStyle(name='event'
            , fontName = 'Calibri'
            , fontSize = 5
            , leading = 5
            , textColor = "#43536a"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_init_value'
            , fontName = 'CalibriBd'
            , fontSize = 12
            , textColor = "#c00101"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_result_title'
            , fontName = 'Calibri'
            , fontSize = 4
            , textColor = "#000000"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_result'
            , fontName = 'Calibri'
            , fontSize = 6
            , textColor = "#000000"
            , alignment=TA_CENTER))

        self.canv.saveState()

        chart = covid_chart()
        chart.x = 0.5 * inch
        chart.y = 0.0 * inch
        chart.height = 4*inch
        chart.width = 8.5*inch

        if self.sir :
            chart.data = [
                self.params["susceptible"],
                self.params["infected"],
                self.params["recovered"],
             ]
        else:
            chart.data = [
                self.params["hosp-sd"],
                self.params["icu-sd"],
                self.params["vent-sd"],
             ]

        if not self.sir :
            series = (
                'MedSurg',
                'ICU',
                'Ventilated',
                )
        else:
            series = (
                'Susceptible Population',
                'Infected',
                'Recovered',
                )
        for i, s in enumerate(series): chart.lines[i].name = s

        lbldates = []
        for dt in self.params["labeled-dates"]:
            lbldates.append(dt[0])

        chart.xValueAxis.strokeWidth = 0.25
        chart.xValueAxis.strokeColor = HexColor("#dddddddd", hasAlpha=True)
        chart.xValueAxis.tickDown = 1 * mm
        chart.xValueAxis.labels.fontName = "Calibri"
        chart.xValueAxis.labels.fontSize = 5
        chart.xValueAxis.labels.angle = -90
        chart.xValueAxis.labels.dx = 3.3
        chart.xValueAxis.labels.dy = -10.0
        chart.xValueAxis.gridStrokeWidth = 0.25
        chart.xValueAxis.gridStrokeColor = HexColor("#dddddddd", hasAlpha=True)
        chart.xValueAxis.visibleGrid = 1
        chart.xValueAxis.xLabelFormat = "{dd}-{mmm}"
        chart.xValueAxis.forceFirstDate = chart.xValueAxis.forceEndDate = True
        chart.xValueAxis.niceMonth = True
        chart.xValueAxis.specifiedTickDates = lbldates

        chart.yValueAxis.strokeWidth = 0.25
        chart.yValueAxis.strokeColor = HexColor("#dddddd")
        chart.yValueAxis.labels.fontName = "Calibri"
        chart.yValueAxis.labels.fontSize = 6
        chart.yValueAxis.labelTextFormat = "{:,.0f}"

        ymax = ((self.params["ymax"] + 25) // 10) * 10

        chart.yValueAxis.valueMin = 0
        chart.yValueAxis.valueMax = ymax
        chart.yValueAxis.valueStep = ymax // 10
        # chart.yValueAxis.dumpProperties()

        chart.lineLabelFormat = self.label_formatter
        chart.lineLabels.fontName = "Calibri"
        chart.lineLabels.fontSize = 5
        chart.lineLabelNudge = 0.05 * inch

        line_colors = [ HexColor("#5c9bd5ff", hasAlpha=True)
                      , HexColor("#ffbf01ff", hasAlpha=True)
                      , HexColor("#c00101ff", hasAlpha=True)]
        line_widths = [ 1.5, 1.5, 1.5, ]

        for idx, color in enumerate(line_colors):
            chart.lines[idx].strokeColor = color
            chart.lines[idx].strokeWidth = line_widths[idx]

        if not self.sir:
            if self.params["hosp-beds"][0][1] > 0:
                lc = len(chart.data)
                chart.data.append( self.params["hosp-beds"] )
                chart.lines[lc].strokeDashArray = ( 1, 1 )
                chart.lines[lc].strokeWidth = 0.5
                chart.lines[lc].strokeColor = HexColor("#335aa2")
                chart.lines[lc].name = "MedSurg Bed Capacity"

            if self.params["icu-beds"][0][1] > 0:
                lc = len(chart.data)
                chart.data.append( self.params["icu-beds"] )
                chart.lines[lc].strokeDashArray = ( 1, 1 )
                chart.lines[lc].strokeWidth = 0.5
                chart.lines[lc].strokeColor = HexColor("#ffbf01")
                chart.lines[lc].name = "ICU Bed Capacity"

            if self.params["vent-beds"][0][1] > 0:
                lc = len(chart.data)
                chart.data.append( self.params["vent-beds"] )
                chart.lines[lc].strokeDashArray = ( 1, 1 )
                chart.lines[lc].strokeWidth = 0.5
                chart.lines[lc].strokeColor = HexColor("#c00101")
                chart.lines[lc].name = "Ventilated Bed Capacity"

        legend = Legend()

        legend.alignment = 'right'
        legend.x = 9.25*inch
        legend.y = 1.0*inch
        legend.colorNamePairs = Auto(obj=chart)
        legend.columnMaximum = 12
        legend.fontName = "Calibri"
        legend.fontSize = 5
        legend.deltay = 1

        d.add(chart, 'graph')

        d.add(legend)

        leftm = (2.67 * 3 - 1) # aligning with the header
        gap = 0.06
        vp  = 0.25
        col = (3 / 5)

        has_medsurg = (self.params['beds'][0] > 0)
        has_icu     = (self.params['beds'][1] > 0)
        has_vent    = (self.params['beds'][2] > 0)

        ladj = 0
        if not has_medsurg: ladj += col
        if not has_icu: ladj += col
        if not has_vent: ladj += col

        self.canv.restoreState()

        d.drawOn( self.canv, 0, 0)

        vp  = 0.25

        self.canv.saveState()

        self.canv.setStrokeColor("#c00101")
        self.canv.setLineWidth(0.25)


        # Mark Today
        day_zero = chart.get_day_x(0)
        self.canv.line(day_zero[0], day_zero[1], day_zero[0], day_zero[2]  )

        p = Paragraph("Today", style=self.styles["today"])
        p.wrapOn(self.canv, 0.75*inch, self.height*2)
        p.drawOn(self.canv, day_zero[0] - 0.1*inch, day_zero[2])

        self.canv.setFillColor("#c00101")
        p = Polygon(points=[
            day_zero[0] + 0.03*inch, day_zero[2] + 0.05*inch,
            day_zero[0] - 0.03*inch, day_zero[2] + 0.05*inch,
            day_zero[0], day_zero[2] - 0.25,
            ])
        p.fillColor = HexColor("#c00101")
        p.strokeColor = HexColor("#ffffff")
        p.strokeWidth = 0.01

        d2.add(p)
        d2.drawOn(self.canv, 0, 0)

        self.canv.setStrokeColor("#43536a")
        for idx, row in self.params["mitigations"].iterrows():

            note = "{i}. {n}".format(i=idx+1, n=row[-1])

            tv = tw = stringWidth(note, "Calibri", 5) / inch
            tw = max( tw, 0.75 * inch ) / 2
            if tv > 0.75:
                tv = 0.125/2 * inch
            else :
                tv = 0.0

            vo = (( 1 + (idx % 10) )*0.125*inch) + (0.5*inch)

            dt = row['mitigation_date']
            day_zero = chart.get_day_x_by_date(dt)
            self.canv.line(day_zero[0], day_zero[1], day_zero[0], day_zero[2] - vo )

            p = Paragraph(note, style=self.styles["event"])
            p.wrapOn(self.canv, 0.75*inch, self.height*2)
            p.drawOn(self.canv, day_zero[0] - tw, day_zero[2] - vo + 0.08*inch)

            self.canv.setFillColor("#43536a")
            p = Polygon(points=[
                day_zero[0] + 0.03*inch, day_zero[2] + 0.05*inch - vo,
                day_zero[0] - 0.03*inch, day_zero[2] + 0.05*inch  - vo,
                day_zero[0], day_zero[2] - 0.25  - vo,
                ])
            p.fillColor = HexColor("#43536a")
            p.strokeColor = HexColor("#ffffff")
            p.strokeWidth = 0.01

            d2.add(p)
            d2.drawOn(self.canv, 0, 0)

        self.canv.translate(-0.5*inch, 2*inch)
        self.canv.rotate(90)
        if self.sir :
            p = Paragraph("Total Impacted Population", style=self.styles["box_header"])
        else:
            p = Paragraph("Daily Inpatient Load (Projected Census)", style=self.styles["box_header"])
        # p.wrapOn(self.canv, 2*inch, self.height*2)
        # p.drawOn(self.canv, *self.coord( 0.75, 2.9, inch))
        p.wrapOn(self.canv, 2*inch, self.height*2)
        p.drawOn(self.canv, *self.coord( -1.5, 4.7, inch))

        self.canv.restoreState()
