# boxy_line.py
from reportlab.lib.units import inch, mm
from reportlab.platypus import Flowable, Paragraph
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, Line

from reportlab.pdfbase.pdfmetrics import stringWidth


class ScenarioHeader(Flowable):

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

        d = Drawing(width=self.width, height=self.height)

        self.styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='CenterAlign', alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_header'
            , fontName = 'CalibriBd'
            , fontSize = 5
            , textColor = "#43536a"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_init'
            , fontName = 'CalibriBd'
            , fontSize = 8
            , textColor = "#c00101"
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

        self.canv.saveState()

        inc = 2.67
        gap = 0.06

        for i in (0, 1, 2, 3):

            d.add(Rect(*self.coord(inc * i, 0.5 + gap, inch), 2 * inch, 0.5*inch
                , strokeColor="#7e7f7f"
                , fillColor="#eeeeee"
                , strokeWidth=0.25
                ))

            d.add(Line(*self.hlinecoord(inc * i, gap, 2, inch)
                , strokeColor="#a2b7e0"
                , strokeWidth=0.5
                ))

            if i > 0:
                d.add(Line(*self.vlinecoord((inc * i) + 1, gap, 0.5, inch)
                    , strokeColor="#7e7f7f"
                    , strokeWidth=0.25
                    ))
                d.add(Line(*self.hlinecoord((inc * i), gap + (1/6), 2, inch)
                    , strokeColor="#7e7f7f"
                    , strokeWidth=0.25
                    ))
                d.add(Line(*self.hlinecoord((inc * i), gap + (2/6), 2, inch)
                    , strokeColor="#7e7f7f"
                    , strokeWidth=0.25
                    ))

            # self.canv.rect(*self.coord(inc * i, 0.5 + gap, inch), 2 * inch, 0.5*inch)

            # self.canv.setLineWidth(0.75)
            # self.canv.setStrokeColor("#a2b7e0")

            # self.canv.line(*self.vlinecoord(inc * i, 0.05, -3, inch))
            # self.canv.line(*self.vlinecoord((inc * i) + 2, 0.05, -3, inch))

        d.drawOn( self.canv, 0, 0)

        for hdr, pos in (('Initial Doubling Time between successive generations', 0 * inc)
            , ('Social Distancing at {:.0%}'.format(self.params["sd0"]), 1 * inc)
            , ('Social Distancing at {:.0%}'.format(self.params["sd1"]), 2 * inc)
            , ('Social Distancing at {:.0%}'.format(self.params["sd2"]), 3 * inc)
            ) :
            p = Paragraph(hdr, style=self.styles["box_header"])
            p.wrapOn(self.canv, 2*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(pos, .125, inch))

        p = Paragraph('{:.1f} days'.format(self.params["dbltime"]), style=self.styles["box_init_value"])
        p.wrapOn(self.canv, 1*inch, self.height*2)
        p.drawOn(self.canv, *self.coord(0, gap + 0.293, inch))

        v = stringWidth(self.params["scenario"], "CalibriBd", 8) / inch
        if v > 1.0:
            v = 0.44
        else:
            v = 0.3335

        p = Paragraph(self.params["scenario"], style=self.styles["box_init"])
        p.wrapOn(self.canv, 1*inch, self.height*2)
        p.drawOn(self.canv, *self.coord(1, gap + v, inch))



        for lbl, xpos, vidx in (("R0", inc, 1)
            ,("Rt", inc, 2)
            ,("Effective Doubling Rate (Days)", inc, 3)
             ):
            vpos = gap + (vidx/6) + .042
            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos, vpos, inch))

            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos + inc , vpos, inch))

            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos + (2*inc) , vpos, inch))

        for lbl, xpos, vidx in (("{:.2f}".format(self.params["sd0_R0"]), inc , 1)
            ,(("{:.2f}".format(self.params["sd0_Rt"]), inc , 2))
            ,(("{:.2f}".format(self.params["sd0_edbl"]), inc, 3))
             ):
            vpos = gap + (vidx/6) + .042
            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos + 1, vpos, inch))

        for lbl, xpos, vidx in (("{:.2f}".format(self.params["sd1_R0"]), 2*inc , 1)
            ,(("{:.2f}".format(self.params["sd1_Rt"]), 2*inc , 2))
            ,(("{:.2f}".format(self.params["sd1_edbl"]), 2*inc, 3))
             ):
            vpos = gap + (vidx/6) + .042
            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos + 1, vpos, inch))

        for lbl, xpos, vidx in (("{:.2f}".format(self.params["sd2_R0"]), 3*inc , 1)
            ,(("{:.2f}".format(self.params["sd2_Rt"]), 3*inc , 2))
            ,(("{:.2f}".format(self.params["sd2_edbl"]), 3*inc, 3))
             ):
            vpos = gap + (vidx/6) + .042
            p = Paragraph(lbl, style=self.styles["box_result_title"])
            p.wrapOn(self.canv, 1*inch, self.height*2)
            p.drawOn(self.canv, *self.coord(xpos + 1, vpos, inch))

        self.canv.restoreState()

class ScenarioInflectedHeader(Flowable):

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
        self.height = inch * 0.3
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

        d = Drawing(width=self.width, height=self.height)

        self.styles.add(ParagraphStyle(name='RightAlign', alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='LeftAlign', alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='CenterAlign', alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='box_header'
            , fontName = 'CalibriBd'
            , fontSize = 5
            , textColor = "#43536a"
            , alignment=TA_CENTER))

        self.styles.add(ParagraphStyle(name='section_inf_subhead'
            , fontName = 'Calibri'
            , fontSize = 6
            , textColor = "#43536a"
            , alignment=TA_LEFT))

        self.styles.add(ParagraphStyle(name='section_inf_head'
            , fontName = 'CalibriBd'
            , fontSize = 12
            , textColor = "#43536a"
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

        self.canv.saveState()

        p = Paragraph("Social Distancing Adjusted for Local Responses", style=self.styles["section_inf_head"])
        p.wrapOn(self.canv, 10*inch, self.height*2)
        p.drawOn(self.canv, *self.coord(0.0, 0.125, inch))

        p = Paragraph("Initial Doubling Time between successive generations: {:0.1f} days ({})".format(self.params["dbltime"], self.params["scenario"]), style=self.styles["section_inf_subhead"])
        p.wrapOn(self.canv, 10*inch, self.height*2)
        p.drawOn(self.canv, *self.coord(0.0, 0.35, inch))

        self.canv.restoreState()
