# Short script that creates a content test page
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

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

c = canvas.Canvas("content-test.pdf", (10*cm, 12*cm))
c.drawString(0, 11.67*cm, "This is a test page!")
c.drawString(0, 0, "This is a test page!")
c.drawCentredString(5*cm, 8*cm, "This is a test page!")
c.drawRightString(10*cm, 11.67*cm, "This is a test page!")
c.drawRightString(10*cm, 0, "This is a test page!")

c.showPage()
c.save()