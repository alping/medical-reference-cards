#!/usr/bin/python

# Class file for generating and printing medical reference cards
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

def xtitle(string):
		return string.title().replace('And', 'and')

class MedRefCardFace():
	"""Medical Reference Card Face"""
	def __init__(self, header, content_path, footer, toc, references):
		self.header = header
		self.content_path = content_path
		self.footer = footer
		self.toc = toc
		self.references = references

	def __repr__(self):
		return repr((self.header, self.content_path, self.footer, self.toc, self.references))


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

		self.domain = card_dict['domain'].lower()
		self.category = card_dict['category'].lower()

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

		def __repr__(self):
			return repr((self.card_folder, self.card_fn, self.domain, self.category, self.modified_date, self.verified_date,
				self.verified_by, self.front_face, self.back_face))


class MedRefDeck():
	"""Medical Reference Card Deck"""

	def __init__(self, localisation, card_filter, content_path):
		self.localisation = localisation
		self.card_filter = card_filter
		self.content_path = os.path.join(content_path, localisation)
		self.cards = []
		self.domain_index = []

		card_files = self.find_all_cards()

		# Create a list of all MedRefCards
		active_domain = ''
		for card_file in card_files:
			self.cards.append(MedRefCard(card_file))
			if self.cards[-1].domain != active_domain:
				self.domain_index.append(self.cards[-1].domain)
				active_domain = self.cards[-1].domain

		logging.info('Deck generated successfully. Number of cards: ' + str(len(self.cards)))

	def __repr__(self):
		return repr((self.localisation, self.card_filter, self.content_path, self.cards))

	def find_all_cards(self):
		pattern = '*.yml'
		path = self.content_path
		result = []
		for root, dirs, files in os.walk(path):
			for name in files:
				if fnmatch.fnmatch(name, pattern):
					result.append(os.path.join(root, name))
		return result

	def sort(self, reverse=False):
		self.cards = sorted(self.cards, key=lambda card: card.domain, reverse=reverse)


class MedRefCards():
	"""Class for generating and printing medical reference cards"""
	def __init__(self, localisation='eng', card_filter='all', content_path='../contents'):
		self.med_ref_deck = self.generate_deck(localisation, card_filter, content_path)
		self.sort_deck()

	def __repr__(self):
		return repr((self.med_ref_deck))

	def generate_deck(self, localisation='eng', card_filter='all', content_path='../contents'):
		return MedRefDeck(localisation, card_filter, content_path)

	def sort_deck(self, reverse=False):
		self.med_ref_deck.sort(reverse)

	def generate_pdf(self, colour_scheme='default-colour-scheme', frame_layout='default-frame-layout',
					 output_folder='../pdf', file_name=None,
					 domain_filter=None, df_invert=False,
					 category_filter=None, cf_invert=False,
					 no_title=False):
		## Colour scheme check
		colour_scheme_path = os.path.join('../theme/colour-schemes', colour_scheme + '.yml')
		if not os.path.isfile(colour_scheme_path):
			logging.warning('No colour scheme: ' + colour_scheme + '. Using colour scheme: default.')
			colour_scheme_path = '../theme/colour-schemes/default-colour-scheme.yml'

		## Frame layout check
		frame_layout_path = os.path.join('../theme/frame-layouts', frame_layout + '.yml')
		if not os.path.isfile(frame_layout_path):
			logging.warning('No frame layout: ' + frame_layout + '. Using frame layout: default.')
			frame_layout_path = '../theme/frame-layouts/default-frame-layout.yml'

		colour_scheme = yaml_loader(colour_scheme_path)
		frame_layout_name = frame_layout
		frame_layout = self.set_frame_layout(yaml_loader(frame_layout_path))

		if file_name is not None:
			output_fn = file_name + '.pdf'
		else:
			output_fn = 'medical-reference-cards' + '-' + frame_layout_name + '-' + self.med_ref_deck.localisation + '.pdf'

		output_path = os.path.join(output_folder, self.med_ref_deck.localisation, output_fn)


		if frame_layout['output'] == 'spread':
			canvas_size = (frame_layout['card_spread']['width']*cm, frame_layout['card_spread']['height']*cm)
			draw_card = self.draw_card_spread
		elif frame_layout['output'] == 'double-sided':
			draw_size = canvas_size = (2*frame_layout['card']['width']*cm, 2*frame_layout['card']['height']*cm)
			draw_card = self.draw_double_sided
		else:
			draw_size = canvas_size = (frame_layout['card']['width']*cm, frame_layout['card']['height']*cm)
			draw_card = self.draw_card_page

		c = canvas.Canvas(output_path, canvas_size, pageCompression = 0)

		if not no_title:
			self.draw_title_page(c, canvas_size[0], canvas_size[1])

		active_domain = ''
		domain_index = []

		if frame_layout['output'] == 'double-sided':
			cards_for_page = []
			for card in self.med_ref_deck.cards:
				if 	category_filter is None or not cf_invert and card.category.lower() in category_filter or cf_invert and card.category.lower() not in category_filter:
					if 	domain_filter is None or not df_invert and card.domain.lower() in domain_filter or df_invert and card.domain.lower() not in domain_filter:
						cards_for_page.append(card)
						if len(cards_for_page) == 4:
							draw_card(c, cards_for_page, colour_scheme, frame_layout)
							cards_for_page = []
			if len(cards_for_page) > 0:
				draw_card(c, cards_for_page, colour_scheme, frame_layout)

		else:
			for card in self.med_ref_deck.cards:
				if 	category_filter is None or not cf_invert and card.category.lower() in category_filter or cf_invert and card.category.lower() not in category_filter:
					if 	domain_filter is None or not df_invert and card.domain.lower() in domain_filter or df_invert and card.domain.lower() not in domain_filter:
						if card.domain != active_domain:
							self.add_toc_item(c, xtitle(card.domain), 'domain-' + card.domain, 1, True)
							domain_index.append(card.domain)
							active_domain = card.domain
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

	def draw_title_page(self, c, width, height):
		title_text = 'Medical Reference Cards'
		subtitle_text = 'github.com/alping/medical-reference-cards'

		c.setFillColorRGB(0, 0, 0)

		# Draw title
		c.setFont('Helvetica-Bold', 20, leading = None)
		c.drawCentredString(width/2, height - 4*cm, title_text)

		# Draw subtitle
		c.setFont('Helvetica-Bold', 8, leading = None)
		c.drawCentredString(width/2, height - 4.5*cm, subtitle_text)

		self.add_toc_item(c, title_text, 'title-page', 0)

		c.showPage()

	def draw_card_spread(self, c, card, colour_scheme, frame_layout):
		self.draw_card_face(c, card.front_face, card.domain, colour_scheme, frame_layout, 1)
		self.draw_card_face(c, card.back_face, card.domain, colour_scheme, frame_layout, 2, frame_layout['card']['width']*cm)
		self.add_toc_item(c, card.front_face.header + ' / ' + card.back_face.header, card.front_face.header + '-' + card.back_face.header, 2, True)

		item_nr = 0

		self.add_toc_item(c, 'Front Face', card.front_face.header + '-front', 3)
		for title in card.front_face.toc:
			if title != '':
				self.add_toc_item(c, title, card.front_face.header + '-' + str(item_nr), 4)
				item_nr += 1

		self.add_toc_item(c, 'Back Face', card.back_face.header + '-back', 3)
		for title in card.back_face.toc:
			if title != '':
				self.add_toc_item(c, title, card.back_face.header + '-' + str(item_nr), 4)
				item_nr += 1

		c.showPage()

	def draw_double_sided(self, c, cards_for_page, colour_scheme, frame_layout):
		guide_width = 0.01*cm

		for add in range(len(cards_for_page)+1, 5):
			cards_for_page.append(None)

		for card_number in range(4,0,-1):
			if card_number % 2 == 0:
				x_offset = frame_layout['card']['width']*cm
			else:
				x_offset = 0

			if card_number > 2:
				y_offset = 0
			else:
				y_offset = frame_layout['card']['height']*cm

			if cards_for_page[card_number-1] is not None:
				self.draw_card_face(c, cards_for_page[card_number-1].front_face, cards_for_page[card_number-1].domain, colour_scheme, frame_layout, 1, x_offset, y_offset)

		c.setFillColorRGB(1, 1, 1)

		c.rect(	frame_layout['card']['width']*cm - guide_width/2, 0,
				guide_width, 2 * frame_layout['card']['height']*cm,
				stroke=0, fill=1)

		c.rect(	0, frame_layout['card']['height']*cm - guide_width/2,
				2 * frame_layout['card']['width']*cm, guide_width,
				stroke=0, fill=1)

		c.showPage()

		for card_number in range(4,0,-1):
			if card_number % 2 == 0:
				x_offset = 0
			else:
				x_offset = frame_layout['card']['width']*cm

			if card_number > 2:
				y_offset = 0
			else:
				y_offset = frame_layout['card']['height']*cm

			if cards_for_page[card_number-1] is not None:
				self.draw_card_face(c, cards_for_page[card_number-1].back_face, cards_for_page[card_number-1].domain, colour_scheme, frame_layout, 2, x_offset, y_offset)

		c.setFillColorRGB(1, 1, 1)

		c.rect(	frame_layout['card']['width']*cm - guide_width/2, 0,
				guide_width, 2 * frame_layout['card']['height']*cm,
				stroke=0, fill=1)

		c.rect(	0, frame_layout['card']['height']*cm - guide_width/2,
				2 * frame_layout['card']['width']*cm, guide_width,
				stroke=0, fill=1)

		c.showPage()

	def draw_card_page(self, c, card, colour_scheme, frame_layout):
		self.add_toc_item(c, card.front_face.header + ' / ' + card.back_face.header, card.front_face.header + '-' + card.back_face.header, 2, True)

		self.draw_card_face(c, card.front_face, card.domain, colour_scheme, frame_layout, 1)
		self.add_toc_item(c, card.front_face.header, card.front_face.header, 3)

		item_nr = 0

		for title in card.front_face.toc:
			if title != '':
				self.add_toc_item(c, title, card.front_face.header + '-' + str(item_nr), 4)
				item_nr += 1

		c.showPage()

		self.draw_card_face(c, card.back_face, card.domain, colour_scheme, frame_layout, 2)
		self.add_toc_item(c, card.back_face.header, card.back_face.header, 3)

		item_nr = 0

		for title in card.back_face.toc:
			if title != '':
				self.add_toc_item(c, title, card.back_face.header + '-' + str(item_nr), 4)
				item_nr += 1

		c.showPage()

	def draw_card_face(self, c, card_face, domain, colour_scheme, frame_layout, face_nr, x_offset = 0, y_offset = 0):
		if domain in colour_scheme:
			colour = (float(colour_scheme[domain][0])/255, float(colour_scheme[domain][1]/255), float(colour_scheme[domain][2]/255))
		else:
			logging.warning('No colour defined for domain: ' + domain + ', in colour scheme.')
			colour = (0.5, 0.5, 0.5)

		nr_of_domains = len(self.med_ref_deck.domain_index)
		this_domain_index = self.med_ref_deck.domain_index.index(domain)

		# Colour frame
		c.setFillColorRGB(colour[0], colour[1], colour[2])
		if frame_layout['footer_index']:
			c.roundRect(0 + x_offset,
						0 + frame_layout['border']['bottom']*cm * 0.4 + y_offset,
						frame_layout['card']['width']*cm,
						frame_layout['card']['height']*cm - frame_layout['border']['bottom']*cm * 0.4,
						radius=frame_layout['border']['outer_corner_radius']*cm, stroke=0, fill=1)

			if this_domain_index == 0 and face_nr == 1 or this_domain_index == nr_of_domains-1 and face_nr == 2:
				c.rect(	0 + x_offset,
						0 + frame_layout['border']['bottom']*cm * 0.4 + y_offset,
						frame_layout['border']['outer_corner_radius']*cm,
						frame_layout['border']['outer_corner_radius']*cm,
						stroke=0, fill=1)

			if this_domain_index == nr_of_domains-1 and face_nr == 1 or this_domain_index == 0 and face_nr == 2:
				c.rect(	frame_layout['border']['left']*cm + frame_layout['content']['width']*cm + frame_layout['border']['right']*cm - frame_layout['border']['outer_corner_radius']*cm + x_offset,
						0 + frame_layout['border']['bottom']*cm * 0.4 + y_offset,
						frame_layout['border']['outer_corner_radius']*cm,
						frame_layout['border']['outer_corner_radius']*cm,
						stroke=0, fill=1)
		else:
			c.roundRect(0 + x_offset, 0 + y_offset, frame_layout['card']['width']*cm, frame_layout['card']['height']*cm, radius=frame_layout['border']['outer_corner_radius']*cm, stroke=0, fill=1)

		# Content space
		c.setFillColorRGB(1, 1, 1)
		c.roundRect(frame_layout['border']['left']*cm - 0*frame_layout['border']['inner_corner_radius']*cm + x_offset,
					frame_layout['border']['bottom']*cm - 0*frame_layout['border']['inner_corner_radius']*cm + y_offset,
					frame_layout['content']['width']*cm + 0*frame_layout['border']['inner_corner_radius']*cm,
					frame_layout['content']['height']*cm + 0*frame_layout['border']['inner_corner_radius']*cm,
					radius=frame_layout['border']['inner_corner_radius']*cm, stroke=0, fill=1)

		# Key ring cut-out: 0 = none, 1 = top left, 2 = top right
		if face_nr == 1:
			c.circle(0 + x_offset, frame_layout['card_spread']['height']*cm + y_offset, frame_layout['key_ring']['radius']*cm, stroke=0, fill=1)
		elif face_nr == 2:
			if frame_layout['output'] == 'double-sided':
				c.circle(frame_layout['card']['width']*cm + x_offset, frame_layout['card']['height']*cm + y_offset, frame_layout['key_ring']['radius']*cm, stroke=0, fill=1)
			else:
				c.circle(frame_layout['card_spread']['width']*cm, frame_layout['card_spread']['height']*cm + y_offset, frame_layout['key_ring']['radius']*cm, stroke=0, fill=1)

		# Domain / Caetgory text
		c.setFont('Helvetica', 10, leading = None)

		c.drawCentredString(frame_layout['card']['width']*cm/2 + x_offset, frame_layout['card']['height']*cm - 0.48*cm + y_offset, '- ' + xtitle(domain) + ' -')

		# Header text
		if len(card_face.header) < 23:
			c.setFont('Helvetica-Bold', 20, leading = None)
		elif len(card_face.header) < 36:
			c.setFont('Helvetica-Bold', 19, leading = None)
		else:
			c.setFont('Helvetica-Bold', 18, leading = None)

		c.drawCentredString(frame_layout['card']['width']*cm/2 + x_offset, frame_layout['card']['height']*cm - 1.2*cm + y_offset, card_face.header)

		# Footer
		if frame_layout['footer_index']:
			width = (frame_layout['border']['left']*cm + frame_layout['content']['width']*cm + frame_layout['border']['right']*cm) / nr_of_domains
			height = frame_layout['border']['bottom']*cm - frame_layout['border']['inner_corner_radius']*cm
			x_pos_1 = x_offset + this_domain_index * width
			x_pos_2 = x_offset + frame_layout['border']['left']*cm + frame_layout['content']['width']*cm + frame_layout['border']['right']*cm - (this_domain_index+1) * width
			y_pos = 0 + y_offset

			c.setFillColorRGB(colour[0], colour[1], colour[2])

			if face_nr == 1:
				c.roundRect(x_pos_1, y_pos, width, height, radius=0.06*cm, stroke=0, fill=1)
			if face_nr == 2:
				c.roundRect(x_pos_2, y_pos, width, height, radius=0.06*cm, stroke=0, fill=1)
		else:
			c.setFillColorRGB(1, 1, 1)
			c.setFont('Helvetica', 7, leading = None)
			c.drawCentredString(frame_layout['card']['width']*cm/2 + x_offset, 0.14*cm + y_offset, frame_layout['static_text']['footer'])

		# Include contents
		if os.path.isfile(card_face.content_path):
			c.setFillColorRGB(0, 0, 0)
			page = pagexobj(PdfReader(card_face.content_path).pages[0])
			c.saveState()
			c.translate(frame_layout['border']['left']*cm + x_offset, frame_layout['border']['bottom']*cm + y_offset)
			c.doForm(makerl(c, page))
			c.restoreState()


if __name__ == '__main__':
	pass;
	# med_ref_cards = MedRefCards()
	# med_ref_cards.generate_pdf(frame_layout='print')

	# med_ref_cards.generate_pdf(frame_layout='print-double-sided', output_folder='../pdf/print-double-sided', category_filter=['basic'], no_title=True)
	# colour_scheme = yaml_loader('../theme/colour-schemes/default-colour-scheme.yml')
	# for key,val in colour_scheme.items():
	# 	med_ref_cards.generate_pdf(frame_layout='print-double-sided', output_folder='../pdf/print-double-sided', file_name=key, domain_filter=[key], category_filter=['basic'], no_title=True)

	# # med_ref_cards.generate_pdf(frame_layout='no-footer')
	# # med_ref_cards.generate_pdf(frame_layout='indexed')
	# med_ref_cards.generate_pdf(frame_layout='screen')
