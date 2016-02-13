from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

## Name of output file
OUTPUT_FN = "medical-reference-cards.pdf"

## Dimensions setup
# Content dimensions (width, height)
CONTENT_DIM = (10*cm, 14*cm)
# Face margins outside of content (top, right, bottom, left)
FACE_MARGINS = (2*cm, 0.2*cm, 0.5*cm, 0.2*cm)
# Size of face, based on content dimensions and Face margins (width, height)
FACE_DIM = (CONTENT_DIM[0] + FACE_MARGINS[1] + FACE_MARGINS[3], CONTENT_DIM[1] + FACE_MARGINS[0] + FACE_MARGINS[2])
# Size of unfolded card, face dimensions (width, height)
DOCUMENT_DIM = (FACE_DIM[0]*2, FACE_DIM[1])
# Size of keyring cut-out (radius)
KEY_RING_RAD = 1.2*cm

# Outer rounded egdes radius
OUTER_ROUNDED_RAD = 0.5*cm
# Outer rounded egdes radius
INNER_ROUNDED_RAD = 0.2*cm

## Static text setup
FOOTER_TEXT = "github.com/alping/medical-reference-cards"

# Creates and populates the a deck of cards
def generate_deck():
	c = canvas.Canvas(OUTPUT_FN, DOCUMENT_DIM)
	
	# Create all the cards in the deck
	create_card(c, "FACE 1", "FACE 2", "We do what we must, because we can. - GLaDOS")
	create_card(c, "FACE 1", "FACE 2", "We do what we must, because we can. - GLaDOS")
	create_card(c, "FACE 1", "FACE 2", "We do what we must, because we can. - GLaDOS")
	
	c.save()

def create_card(c, header_front, header_back, quote="", frame_colour=(0.2,0.5,0.3)):
	create_front_face(c, header_front, FOOTER_TEXT, frame_colour, "content-test.pdf")
	create_back_face(c, header_back, quote, frame_colour, "content-test.pdf")
	c.showPage()

def create_front_face(c, header_text, footer_text, frame_colour, content_pdf_fn):
	# Colour frame
	c.setFillColorRGB(frame_colour[0], frame_colour[1], frame_colour[2])
	c.roundRect(0, 0, FACE_DIM[0], FACE_DIM[1], radius=OUTER_ROUNDED_RAD, stroke=0, fill=1)

	# Content space
	c.setFillColorRGB(1, 1, 1)
	c.roundRect(FACE_MARGINS[3], FACE_MARGINS[2], CONTENT_DIM[0], CONTENT_DIM[1], radius=INNER_ROUNDED_RAD, stroke=0, fill=1)

	# Keyring cut-out, upper left/right corner, depending on page side
	c.circle(0, DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)

	# Header text
	c.setFont("Helvetica", 24, leading = None)
	c.drawCentredString(FACE_DIM[0]/2, FACE_DIM[1] - 1.3*cm, header_text)

	# Footer text
	c.setFont("Helvetica", 8, leading = None)
	c.drawCentredString(FACE_DIM[0]/2, 0.15*cm, footer_text)

	# Include contents
	c.setFillColorRGB(0, 0, 0)
	page = pagexobj(PdfReader(content_pdf_fn).pages[0])
	c.saveState()
	c.translate(FACE_MARGINS[3], FACE_MARGINS[2])
	c.doForm(makerl(c, page))
	c.restoreState()

def create_back_face(c, header_text, footer_text, frame_colour, content_pdf_fn):
	# Colour frame
	c.setFillColorRGB(frame_colour[0], frame_colour[1], frame_colour[2])
	c.roundRect(FACE_DIM[0], 0, FACE_DIM[0], FACE_DIM[1], radius=OUTER_ROUNDED_RAD, stroke=0, fill=1)

	# Content space
	c.setFillColorRGB(1, 1, 1)
	c.roundRect(FACE_DIM[0] + FACE_MARGINS[3], FACE_MARGINS[2], CONTENT_DIM[0], CONTENT_DIM[1], radius=INNER_ROUNDED_RAD, stroke=0, fill=1)

	# Keyring cut-out, upper left/right corner, depending on page side
	c.circle(DOCUMENT_DIM[0], DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)

	# Header text
	c.setFont("Helvetica", 24, leading = None)
	c.drawCentredString(FACE_DIM[0] + FACE_DIM[0]/2, FACE_DIM[1] - 1.3*cm, header_text)

	# Footer text
	c.setFont("Helvetica", 8, leading = None)
	c.drawCentredString(FACE_DIM[0] + FACE_DIM[0]/2, 0.15*cm, footer_text)

	# Include contents
	c.setFillColorRGB(0, 0, 0)
	page = pagexobj(PdfReader(content_pdf_fn).pages[0])
	c.saveState()
	c.translate(FACE_DIM[0] + FACE_MARGINS[3], FACE_MARGINS[2])
	c.doForm(makerl(c, page))
	c.restoreState()

if __name__ == "__main__":
	generate_deck()

# Reportlab userguide: http://www.reportlab.com/docs/reportlab-userguide.pdf
