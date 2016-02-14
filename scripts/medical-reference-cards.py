# Short script that compiles a deck of reference cards for use in medical care
# Copyright (C) 2016 Peter Alping
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Peter Alping
# peter@alping.se

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

## Paths
# Output file path
OUTPUT_FN = '../pdf/medical-reference-cards.pdf'
# Content file path
CONTENT_PATH = '../content'

## Domain colour codes
DOMAIN_COLOURS_FN = '../formatting/domain-colours.yml'
COLOURS = yaml_loader(DOMAIN_COLOURS_FN)

## Dimensions setup
# Content dimensions (width, height)
CONTENT_DIM = (10*cm, 13*cm)
# Face margins outside of content (top, right, bottom, left)
FACE_MARGINS = (1.5*cm, 0.25*cm, 0.5*cm, 0.25*cm)
# Size of face, based on content dimensions and Face margins (width, height)
FACE_DIM = (CONTENT_DIM[0] + FACE_MARGINS[1] + FACE_MARGINS[3], CONTENT_DIM[1] + FACE_MARGINS[0] + FACE_MARGINS[2])
# Size of unfolded card, face dimensions (width, height)
DOCUMENT_DIM = (FACE_DIM[0]*2, FACE_DIM[1])
# Size of key ring cut-out (radius)
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
    path = CONTENT_PATH
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

# Creates and populates the a deck of cards
def generate_deck(output='print'):
	# Find all yaml files describing cards
	cards_yml = find_all_cards()
	
	# Create a list of all cards and add 'path' and 'handle' to dictionary
	cards = []
	for card in cards_yml:
		tmp = yaml_loader(card)
		# Remove file name and .yml extention to create path
		reg_ex = re.search(r'(?P<path>.*/).+\.yml', card)
		tmp['path'] = reg_ex.group('path')
		# Remove file path and .yml extention to create handle
		reg_ex = re.search(r'.*/(?P<handle>.+)\.yml', card)
		tmp['handle'] = reg_ex.group('handle')
		cards.append(tmp)

	if output == 'screen':
		c = canvas.Canvas(OUTPUT_FN, FACE_DIM)
		# Create all the cards in the deck
		for card in cards:
			create_screen_card(c, card['path'], card['handle'], card['domain'], card['category'], card['header_front'], card['header_back'], card['footer_front'], card['footer_back'])
	else:
		c = canvas.Canvas(OUTPUT_FN, DOCUMENT_DIM)
		# Create all the cards in the deck
		for card in cards:
			create_print_card(c, card['path'], card['handle'], card['domain'], card['category'], card['header_front'], card['header_back'], card['footer_front'], card['footer_back'])
	
	c.save()

	return('Deck generated successfully. Number of cards: 1.')

def create_print_card(c, path, handle, domain, category, header_front, header_back, footer_front, footer_back):
	create_card_face(c, domain, category, header_front, FOOTER_TEXT, COLOURS[domain], path + handle + '-front.pdf')
	create_card_face(c, domain, category, header_back, FOOTER_TEXT, COLOURS[domain],  path + handle + '-back.pdf', FACE_DIM[0], 2)
	c.showPage()

def create_screen_card(c, path, handle, domain, category, header_front, header_back, footer_front, footer_back):
	create_card_face(c, domain, category, header_front, FOOTER_TEXT, COLOURS[domain], path + handle + '-front.pdf', 0, 0)
	c.showPage()
	create_card_face(c, domain, category, header_back, FOOTER_TEXT, COLOURS[domain],  path + handle + '-back.pdf', 0, 0)
	c.showPage()

def create_card_face(c, domain, category, header_text, footer_text, frame_colour, content_pdf_fn, offset=0, key_ring=1):
	# Colour frame
	c.setFillColorRGB(frame_colour[0], frame_colour[1], frame_colour[2])
	c.roundRect(0 + offset, 0, FACE_DIM[0], FACE_DIM[1], radius=OUTER_ROUNDED_RAD, stroke=0, fill=1)

	# Content space
	c.setFillColorRGB(1, 1, 1)
	c.roundRect(FACE_MARGINS[3] + offset, FACE_MARGINS[2], CONTENT_DIM[0], CONTENT_DIM[1], radius=INNER_ROUNDED_RAD, stroke=0, fill=1)

	# Key ring cut-out, 0 = none, 1 = left, 2 = right
	if key_ring == 1:
		c.circle(0, DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)
	elif key_ring == 2:
		c.circle(DOCUMENT_DIM[0], DOCUMENT_DIM[1], KEY_RING_RAD, stroke=0, fill=1)

	# Domain / Caetgory text
	c.setFont('Helvetica', 10, leading = None)
	c.drawCentredString(FACE_DIM[0]/2 + offset, FACE_DIM[1] - 0.47*cm, '- ' + domain.title() + ' -')
	# c.drawCentredString(FACE_DIM[0]/2 + offset, FACE_DIM[1] - 0.47*cm, domain.title() + ' / ' + category.title())

	# Header text
	c.setFont('Helvetica-Bold', 20, leading = None)
	c.drawCentredString(FACE_DIM[0]/2 + offset, FACE_DIM[1] - 1.23*cm, header_text)

	# Footer text
	c.setFont('Helvetica', 8, leading = None)
	c.drawCentredString(FACE_DIM[0]/2 + offset, 0.15*cm, footer_text)

	# Include contents
	c.setFillColorRGB(0, 0, 0)
	page = pagexobj(PdfReader(content_pdf_fn).pages[0])
	c.saveState()
	c.translate(FACE_MARGINS[3] + offset, FACE_MARGINS[2])
	c.doForm(makerl(c, page))
	c.restoreState()

if __name__ == '__main__':
	print(generate_deck())

# Reportlab userguide: http://www.reportlab.com/docs/reportlab-userguide.pdf
