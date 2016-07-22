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

import sys, argparse, getopt, logging
import MedRefCards

def main(argv):
	name = ''
	colour_scheme = 'default-colour-scheme'
	frame_layout = 'default-frame-layout'
	card_filter = 'all'
	localisation  = 'eng'
	content_path = '../contents'
	output_path = '../pdf'


	parser = argparse.ArgumentParser(description='Create medical reference cards.')
	parser.add_argument('-n',	'--name',			action='store',			dest='name',			default='',							help='-not in use-')
	parser.add_argument('-c',	'--colour-scheme',	action='store',			dest='colour_scheme',	default='default-colour-scheme',	help='colour scheme')
	parser.add_argument('-f',	'--frame-layout',	action='store',			dest='frame_layout',	default='default-frame-layout',		help='frame layout')
	parser.add_argument('-l',	'--localisation',	action='store',			dest='localisation',	default='eng',						help='localisation')
	parser.add_argument(		'--card-filter',	action='store',			dest='card_filter',		default='all', 						help='card filter')
	parser.add_argument(		'--content-path',	action='store',			dest='content_path',	default='../contents',				help='content path')
	parser.add_argument(		'--output-path',	action='store',			dest='output_path',		default='../pdf',					help='output path')
	parser.add_argument(		'--licence',		action='store_true',	dest='licence',			default=False,						help='show licence')

	args = parser.parse_args()

	if args.licence:
		print('GNU General Public License (http://www.gnu.org/licenses/)')
		return

	med_ref_cards = MedRefCards.MedRefCards(args.localisation, args.card_filter, args.content_path)
	med_ref_cards.generate_pdf(args.colour_scheme, args.frame_layout, args.output_path)

if __name__ == "__main__":
	main(sys.argv[1:])
