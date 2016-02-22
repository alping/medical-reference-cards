#!/usr/bin/python

# Script for generating medical reference cards from the command line
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

import sys, getopt, logging
import MedRefCards

def main(argv):
	name = ''
	colour_scheme = 'default-colour-scheme'
	frame_layout = 'default-frame-layout'
	card_filter = 'all'
	content_path = '../contents'
	output_path = '../pdf'

	options = 'ncfhl'
	long_options = ['name',
					'colour-scheme',
					'frame-layout',
					'card-filter',
					'content-path',
					'output-path',
					'help',
					'licence']

	try:
		opts, args = getopt.getopt(argv, options, long_options)
	except getopt.GetoptError:
		logging.error('Invalid arguments')
		sys.exit(2)

	print(opts)

	for opt, arg in opts:
		if opt in ('-n', '--name'):
			name = arg
		elif opt in ('-c', '--colour-scheme'):
			colour_scheme = arg
		elif opt in ('-f', '--frame-layout'):
			frame_layout = arg
		elif opt in ('--card-filter'):
			card_filter = arg
		elif opt in ('--content-path'):
			content_path = arg
		elif opt in ('--output-path'):
			output_path = arg
		elif opt in ('-h', '--help'):
			print('Short options: ' + options)
			print('Long options: ' + str(long_options))
			return
		elif opt in ('-l', '--licence'):
			print('GNU General Public License (http://www.gnu.org/licenses/)')
			return

	med_ref_cards = MedRefCards.MedRefCards(card_filter, content_path)
	med_ref_cards.generate_pdf(colour_scheme, frame_layout, output_path)

if __name__ == "__main__":
	main(sys.argv[1:])