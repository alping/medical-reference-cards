# Used for finding all the yaml files corresponding to the cards in the content folder
import os, fnmatch, re

# Uses yaml to process yaml files with card information
import yaml

# Uses reportlab to generate the colour frame and the header/footer
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Uses pdfrw to include the contents of each card face, saved as separate pdf:s
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl

# Load and return yaml data
def yaml_loader(filepath):
	with open(filepath, 'r') as file_descriptor:
		data = yaml.load(file_descriptor)
		file_descriptor.close()
	return data

# Dump yaml data to file
def yaml_dump(filepath, data):
	with open(filepath, 'w') as file_descriptor:
		yaml.dump(data, file_descriptor)
		file_descriptor.close()

## Name of output file
OUTPUT_FN = '../pdf/medical-reference-cards.pdf'

## Domain colour codes
DOMAIN_COLOURS_FN = '../formatting/domain-colours.yml'
COLOURS = yaml_loader(DOMAIN_COLOURS_FN)

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
FOOTER_TEXT = 'github.com/alping/medical-reference-cards'

## Go through all files in content folder to identify all cards yaml files
## Source: http://stackoverflow.com/questions/1724693/find-a-file-in-python
def find_all_cards():
    pattern = '*.yml'
    path = '../content'
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

# Creates and populates the a deck of cards
def generate_deck():
	# Find all yaml files describing cards
	cards_yml = find_all_cards()
	
	# Create a list of all cards and add set dict. word 'handle' to be the filename of the yaml file
	cards = []
	for card in cards_yml:
		tmp = yaml_loader(card)
		# Remove file path and .yml extention
		reg_ex = re.search(r'.*/(?P<handle>.+)\.yml', card)
		tmp['handle'] = reg_ex.group('handle')
		cards.append(tmp)

	c = canvas.Canvas(OUTPUT_FN, DOCUMENT_DIM)
	
	# Create all the cards in the deck
	for card in cards:
		create_card(c, card['domain'], card['category'], card['header_front'], card['header_back'], card['footer_front'], card['footer_back'], COLOURS[card['domain']])
	
	c.save()

	return('Deck generated successfully. Number of cards: 1.')

def create_card(c, domain, category, header_front, header_back, footer_front, footer_back, frame_colour=(0.1,0.1,0.1)):
	create_front_face(c, domain, category, header_front, FOOTER_TEXT, frame_colour, 'content-test.pdf')
	create_back_face(c, domain, category, header_back, FOOTER_TEXT, frame_colour, 'content-test.pdf')
	c.showPage()

def create_front_face(c, domain, category, header_text, footer_text, frame_colour, content_pdf_fn):
	# Colour frame
	c.setFillColorRGB(frame_colour[0], frame_colour[1], frame_colour[2])
	c.roundRect(0, 0, FACE_DIM[0], FACE_DIM[1], radius=OUTER_ROUNDED_RAD, stroke=0, fill=1)

	# Content space
	c.setFillColorRGB(1, 1, 1)
	c.roundRect(FACE_MARGINS[3], FACE_MARGINS[2], CONTENT_DIM[0], CONTENT_DIM[1], radius=INNER_ROUNDED_RAD, stroke=0, fill=1)

	# Keyring cut-out, upper left/right corner, depending on page side
	c.circle(0, DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)

	# Domain / Caetgory text
	c.setFont('Helvetica', 14, leading = None)
	c.drawCentredString(FACE_DIM[0]/2, FACE_DIM[1] - 0.7*cm, domain.title() + ' / ' + category.title())

	# Header text
	c.setFont('Helvetica', 24, leading = None)
	c.drawCentredString(FACE_DIM[0]/2, FACE_DIM[1] - 1.6*cm, header_text)

	# Footer text
	c.setFont('Helvetica', 8, leading = None)
	c.drawCentredString(FACE_DIM[0]/2, 0.15*cm, footer_text)

	# Include contents
	c.setFillColorRGB(0, 0, 0)
	page = pagexobj(PdfReader(content_pdf_fn).pages[0])
	c.saveState()
	c.translate(FACE_MARGINS[3], FACE_MARGINS[2])
	c.doForm(makerl(c, page))
	c.restoreState()

def create_back_face(c, domain, category, header_text, footer_text, frame_colour, content_pdf_fn):
	# Colour frame
	c.setFillColorRGB(frame_colour[0], frame_colour[1], frame_colour[2])
	c.roundRect(FACE_DIM[0], 0, FACE_DIM[0], FACE_DIM[1], radius=OUTER_ROUNDED_RAD, stroke=0, fill=1)

	# Content space
	c.setFillColorRGB(1, 1, 1)
	c.roundRect(FACE_DIM[0] + FACE_MARGINS[3], FACE_MARGINS[2], CONTENT_DIM[0], CONTENT_DIM[1], radius=INNER_ROUNDED_RAD, stroke=0, fill=1)

	# Keyring cut-out, upper left/right corner, depending on page side
	c.circle(DOCUMENT_DIM[0], DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)

	# Domain / Caetgory text
	c.setFont('Helvetica', 14, leading = None)
	c.drawCentredString(FACE_DIM[0] + FACE_DIM[0]/2, FACE_DIM[1] - 0.7*cm, domain.title() + ' / ' + category.title())

	# Header text
	c.setFont('Helvetica', 24, leading = None)
	c.drawCentredString(FACE_DIM[0] + FACE_DIM[0]/2, FACE_DIM[1] - 1.6*cm, header_text)

	# Footer text
	c.setFont('Helvetica', 8, leading = None)
	c.drawCentredString(FACE_DIM[0] + FACE_DIM[0]/2, 0.15*cm, footer_text)

	# Include contents
	c.setFillColorRGB(0, 0, 0)
	page = pagexobj(PdfReader(content_pdf_fn).pages[0])
	c.saveState()
	c.translate(FACE_DIM[0] + FACE_MARGINS[3], FACE_MARGINS[2])
	c.doForm(makerl(c, page))
	c.restoreState()

if __name__ == '__main__':
	print(generate_deck())

# Reportlab userguide: http://www.reportlab.com/docs/reportlab-userguide.pdf
