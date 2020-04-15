import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import TABLOID

OUTPUT_DIR = './Dropbox/COVID19/chime-penn-1.1.0/src/pdfgenerator/'
PDF_ASSETS = './Dropbox/COVID19/chime-penn-1.1.0/src/pdfgenerator/assets/'

def add_logos(c):
    print( "adding logos")
    c.translate(0.25*inch, 0.25*inch)
    c.drawImage( PDF_ASSETS + "dha_logo.png", 0, 16*inch, 0.5*inch, 0.5*inch )
    c.drawImage( PDF_ASSETS + "ncr_logo.png", 10*inch, 16*inch, 0.5*inch, 0.5*inch )
    c.translate(0, 0)


def hello(c):
    # move the origin up and to the left
    c.translate(inch,inch)
    # define a large font
    c.setFont("Helvetica", 14)
    # choose some colors
    c.setStrokeColorRGB(0.2,0.5,0.3)
    c.setFillColorRGB(1,0,1) # draw some lines
    c.line(0,0,0,1.7*inch)
    c.line(0,0,1*inch,0)
    # draw a rectangle
    c.rect(0.2*inch,0.2*inch,1*inch,1.5*inch, fill=1)
    # make text go straight up
    c.rotate(90)
    # change color
    c.setFillColorRGB(0,0,0.77)
    # say hello (note after rotate the y coord needs to be negative!)
    c.drawString(0.3*inch, -inch, "Hello World")

c = canvas.Canvas(OUTPUT_DIR + "hello.pdf", pagesize=TABLOID)

add_logos(c)
hello(c)

c.showPage()
c.save()


os.system('open ' + OUTPUT_DIR + 'hello.pdf')
