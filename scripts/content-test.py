from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

c = canvas.Canvas("content-test.pdf", (10*cm, 14*cm))
c.drawString(0, 13.67*cm, "This is a test page!")
c.drawString(0, 0, "This is a test page!")
c.drawCentredString(5*cm, 12*cm, "This is a test page!")
c.drawRightString(10*cm, 13.67*cm, "This is a test page!")
c.drawRightString(10*cm, 0, "This is a test page!")

c.showPage()
c.save()