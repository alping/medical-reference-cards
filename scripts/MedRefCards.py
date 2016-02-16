# Class file for generating and printing medical reference cards.
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

# Used for finding all the yaml files corresponding to the cards in the content folder and for logging
import os, fnmatch, re, logging

# Uses yaml to process yaml files with card information
import yaml

# Uses reportlab to generate the colour frame and the header/footer
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Uses pdfrw to include the contents of each card, saved as separate pdf:s
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


class MedRefCardFace():
	"""Medical Reference Card Face"""
	def __init__(self, header, content_path, footer, toc, references):
		self.header = header
		self.content_path = content_path
		self.footer = footer


class MedRefCard():
	"""Medical Reference Card"""
	def __init__(self, card_file):
		card_dict = yaml_loader(card_file)

		# Remove file name and .yml extention to create path
		path_reg_ex = re.search(r'(?P<path>.*/).+\.yml', card_file)
		# Remove file path and .yml extention to create filename
		fn_reg_ex = re.search(r'.*/(?P<fn>.+)\.yml', card_file)

		self.card_folder = path_reg_ex.group('path')
		self.card_fn = fn_reg_ex.group('fn')
		
		self.domain = card_dict['domain']
		self.category = card_dict['category']

		self.modified_date = card_dict['modified_date']
		self.verified_date = card_dict['verified_date']
		self.verified_by = card_dict['verified_by']

		self.front_face = MedRefCardFace(
			card_dict['front_header'],
			os.path.join(self.card_folder, self.card_fn + '-front.pdf'),
			card_dict['front_footer'],
			card_dict['front_toc'],
			card_dict['front_references']
		)

		self.back_face = MedRefCardFace(
			card_dict['back_header'],
			os.path.join(self.card_folder, self.card_fn + '-back.pdf'),
			card_dict['back_footer'],
			card_dict['back_toc'],
			card_dict['back_references']
		)


class MedRefDeck():
	"""Medical Reference Card Deck"""

	def __init__(self, card_filter, content_path):
		self.card_filter = card_filter
		self.content_path = content_path
		self.cards = []

		card_files = self.find_all_cards()

		# Create a list of all MedRefCards
		for card_file in card_files:
			self.cards.append(MedRefCard(card_file))

		logging.info('Deck generated successfully. Number of cards: ' + str(len(self.cards)))

	def find_all_cards(self):
		pattern = '*.yml'
		path = self.content_path
		result = []
		for root, dirs, files in os.walk(path):
			for name in files:
				if fnmatch.fnmatch(name, pattern):
					result.append(os.path.join(root, name))
		return result


class MedRefCards():
	"""Class for generating and printing medical reference cards"""
	def __init__(self, card_filter='all', content_path='../contents'):
		self.generate_deck(card_filter, content_path)
		
	def generate_deck(self, card_filter='all', content_path='../contents'):
		self.med_ref_deck = MedRefDeck(card_filter, content_path)

	def generate_pdf(self, spread=True, colour_scheme='default', frame_layout='default', output_folder='../pdf'):
		## Colour scheme check
		colour_scheme_path = os.path.join('../theme/colour-schemes', colour_scheme + '.yml')
		if not os.path.isfile(colour_scheme_path):
			logging.warning('No colour scheme: ' + colour_scheme + '. Using colour scheme: default.')
			colour_scheme_path = '../theme/colour-schemes/default.yml'

		## Frame layout check
		frame_layout_path = os.path.join('../theme/frame-layouts', frame_layout + '.yml')
		if not os.path.isfile(frame_layout_path):
			logging.warning('No frame layout: ' + frame_layout + '. Using frame layout: default.')
			frame_layout_path = '../theme/frame-layouts/default.yml'

		if spread:
			output_fn = 'medical-reference-cards' + '-spread'
		else:
			output_fn = 'medical-reference-cards' + '-page'

		output_fn = output_fn + '-' + frame_layout + '.pdf'

		output_path = os.path.join(output_folder, output_fn)

		colour_scheme = yaml_loader(colour_scheme_path)
		frame_layout = self.set_frame_layout(yaml_loader(frame_layout_path))

		if spread:
			canvas_size = (frame_layout['card_spread']['width']*cm, frame_layout['card_spread']['height']*cm)
			draw_card = self.draw_card_spread
		else:
			draw_size = canvas_size = (frame_layout['card']['width']*cm, frame_layout['card']['height']*cm)
			draw_card = self.draw_card_page

		c = canvas.Canvas(output_path, canvas_size)

		self.draw_front_page(c, canvas_size[0], canvas_size[1])
		for card in self.med_ref_deck.cards:
			draw_card(c, card, colour_scheme, frame_layout)

		c.save()

	def set_frame_layout(self, frame_layout):
		frame_layout['card'] = {
			'width': frame_layout['border']['left'] + frame_layout['content']['width'] + frame_layout['border']['right'],
			'height': frame_layout['border']['top'] + frame_layout['content']['height'] + frame_layout['border']['bottom']
		}

		frame_layout['card_spread'] = {
			'width': 2 * frame_layout['card']['width'],
			'height': frame_layout['card']['height']
		}

		return frame_layout

	def add_toc_item(self, c, title, key, level=0, closed=None):
		c.bookmarkPage(key)
		c.addOutlineEntry(title, key, level, closed)

	def draw_front_page(self, c, width, height):
		title_text = 'Medical Reference Cards'
		subtitle_text = 'github.com/alping/medical-reference-cards'

		c.setFillColorRGB(0, 0, 0)

		# Draw title
		c.setFont('Helvetica-Bold', 20, leading = None)
		c.drawCentredString(width/2, height - 4*cm, title_text)

		# Draw subtitle
		c.setFont('Helvetica-Bold', 8, leading = None)
		c.drawCentredString(width/2, height - 4.5*cm, subtitle_text)

		self.add_toc_item(c, 'Medical Reference Cards', 'medical-reference-cards', 0)

		c.showPage()

	def draw_card_spread(self, c, card, colour_scheme, frame_layout):
		self.draw_card_face(c, card.front_face, card.domain, colour_scheme, frame_layout, 1)
		self.draw_card_face(c, card.back_face, card.domain, colour_scheme, frame_layout, 2, frame_layout['card']['width']*cm)
		self.add_toc_item(c, card.front_face.header + ' / ' + card.back_face.header, card.front_face.header + '-' + card.back_face.header, 1)
		c.showPage()

	def draw_card_page(self, c, card, colour_scheme, frame_layout):
		self.add_toc_item(c, card.front_face.header + ' / ' + card.back_face.header, card.front_face.header + '-' + card.back_face.header, 1, True)

		self.draw_card_face(c, card.front_face, card.domain, colour_scheme, frame_layout, 1)
		self.add_toc_item(c, card.front_face.header, card.front_face.header, 2)
		c.showPage()

		self.draw_card_face(c, card.back_face, card.domain, colour_scheme, frame_layout, 2)
		self.add_toc_item(c, card.back_face.header, card.back_face.header, 2)
		c.showPage()

	def draw_card_face(self, c, card_face, domain, colour_scheme, frame_layout, page_nr, offset = 0):
		colour = colour_scheme[domain]

		# Colour frame
		c.setFillColorRGB(colour[0], colour[1], colour[2])
		c.roundRect(0 + offset, 0, frame_layout['card']['width']*cm, frame_layout['card']['height']*cm, radius=frame_layout['border']['outer_corner_radius']*cm, stroke=0, fill=1)

		# Content space
		c.setFillColorRGB(1, 1, 1)
		c.roundRect(frame_layout['border']['left']*cm + offset, frame_layout['border']['bottom']*cm, frame_layout['content']['width']*cm, frame_layout['content']['height']*cm, radius=frame_layout['border']['inner_corner_radius']*cm, stroke=0, fill=1)

		# Key ring cut-out: 0 = none, 1 = top left, 2 = top right
		if page_nr == 1:
			c.circle(0, frame_layout['card_spread']['height']*cm, frame_layout['key_ring']['radius']*cm, stroke=0, fill=1)
		elif page_nr == 2:
			c.circle(frame_layout['card_spread']['width']*cm, frame_layout['card_spread']['height']*cm, frame_layout['key_ring']['radius']*cm, stroke=0, fill=1)

		# Domain / Caetgory text
		c.setFont('Helvetica', 10, leading = None)
		c.drawCentredString(frame_layout['card']['width']*cm/2 + offset, frame_layout['card']['height']*cm - 0.47*cm, '- ' + domain.title() + ' -')

		# Header text
		c.setFont('Helvetica-Bold', 20, leading = None)
		c.drawCentredString(frame_layout['card']['width']*cm/2 + offset, frame_layout['card']['height']*cm - 1.23*cm, card_face.header)

		# Footer text
		c.setFont('Helvetica', 8, leading = None)
		c.drawCentredString(frame_layout['card']['width']*cm/2 + offset, 0.15*cm, frame_layout['static_text']['footer'])

		# Include contents
		c.setFillColorRGB(0, 0, 0)
		page = pagexobj(PdfReader(card_face.content_path).pages[0])
		c.saveState()
		c.translate(frame_layout['border']['left']*cm + offset, frame_layout['border']['bottom']*cm)
		c.doForm(makerl(c, page))
		c.restoreState()


if __name__ == '__main__':
	med_ref_cards = MedRefCards()
	med_ref_cards.generate_deck()
	med_ref_cards.generate_pdf(spread=True, frame_layout='print', output_folder='../pdf/print')
	med_ref_cards.generate_pdf(spread=False, frame_layout='screen', output_folder='../pdf/screen')