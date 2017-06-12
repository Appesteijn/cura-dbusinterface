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

from PyQt5.QtCore import pyqtSignal, pyqtSlot, pyqtProperty, Q_CLASSINFO, QObject, QUrl
from PyQt5.QtDBus import QDBusAbstractAdaptor, QDBusConnection

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.OutputDevice.OutputDeviceManager import OutputDeviceManager

class DBusInterface(QObject, Extension):
    def __init__(self, parent = None):
        super().__init__(parent = parent)

        session_bus = QDBusConnection.sessionBus()

        if not session_bus.registerService("nl.ultimaker.cura"):
            UM.Logger.log("w", "Could not register D-Bus service")
            return

        self._application_adaptor = _ApplicationAdaptor(self)
        session_bus.registerObject("/Application", self._application_adaptor, QDBusConnection.ExportAllContents)

        self._backend_adaptor = _BackendAdaptor(self)
        session_bus.registerObject("/Backend", self._backend_adaptor, QDBusConnection.ExportAllContents)


class _ApplicationAdaptor(QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "nl.ultimaker.cura.Application")

    @pyqtSlot(str)
    def openFile(self, file_path):
        Application.getInstance().readLocalFile(QUrl.fromLocalFile(file_path))

    @pyqtSlot()
    def quit(self):
        Application.getInstance().quit()

    @pyqtProperty(str)
    def versionString(self):
        return Application.getInstance().getVersion()

class _BackendAdaptor(QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "nl.ultimaker.cura.Backend")

    def __init__(self, parent):
        super().__init__(parent)

        self._backend = Application.getInstance().getBackend()

    @pyqtSlot()
    def slice(self):
        self._backend.forceSlice()

    @pyqtProperty(str)
    def state(self):
        return "unknown"

    @pyqtProperty(int)
    def progress(self):
        return -1
