# Short script for testing yaml functionality
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


import yaml

def yaml_loader(filepath):
	with open(filepath, 'r') as file_descriptor:
		data = yaml.load(file_descriptor)
		file_descriptor.close()
	return data

def yaml_dump(filepath, data):
	with open(filepath, 'w') as file_descriptor:
		yaml.dump(data, file_descriptor)
		file_descriptor.close()

if __name__ == "__main__":
	filepath = "../content/pediatrics/general/pediatrics-normal-physiology/pediatrics-normal-physiology.yml"
	data = yaml_loader(filepath)
	print(data)