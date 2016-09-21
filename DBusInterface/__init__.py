'''
    This file is part of cura-dbusinterface.
    Copyright (C) 2016 Arjen Hiemstra <ahiemstra@heimr.nl>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from . import DBusInterface

def getMetaData():
    return {
        "plugin": {
            "name": "D-Bus Interface",
            "author": "Arjen Hiemstra",
            "version": "1.0",
            "description": "Exposes Cura on D-Bus to provide remote control capabilities.",
            "api": 3
        },
    }

def register(app):
    return { "extension": DBusInterface.DBusInterface() }