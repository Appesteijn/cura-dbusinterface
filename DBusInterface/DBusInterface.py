"""
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
"""
import os

from PyQt5.QtCore import pyqtSlot, pyqtProperty, Q_CLASSINFO, QObject, QUrl
from PyQt5.QtDBus import QDBusAbstractAdaptor, QDBusConnection, QDBusMessage

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger

from cura.Settings.ProfilesModel import ProfilesModel


class DBusInterface(QObject, Extension):
    DEFAULT_SESSION_ID = "nl.ultimaker.cura"

    def __init__(self, parent = None):
        super().__init__(parent = parent)

        # Use environment variable to optionally assign a unique session ID to a Cura instance so they won't interfere
        # with each other on the same channel.
        self._extra_session_id = os.environ.get("CURA_DEBUG_DBUS_SESSION_ID", "").strip()
        if self._extra_session_id:
            self._extra_session_id = "." + self._extra_session_id
        self._service_id = self.DEFAULT_SESSION_ID + self._extra_session_id

        self._session_bus = QDBusConnection.sessionBus()
        if not self._session_bus.isConnected():
            Logger.log("e", "Could not connect to D-Bus")
            return

        Logger.log("i", "Registering D-Bus service [%s] ...", self._service_id)
        if not self._session_bus.registerService(self._service_id):
            Logger.log("e", "Could not register D-Bus service [%s]", self._service_id)
            return

        self._application_adaptor = _ApplicationAdaptor(self)
        self._session_bus.registerObject("/Application", self._application_adaptor, QDBusConnection.ExportAllContents)

        self._backend_adaptor = _BackendAdaptor(self)
        self._session_bus.registerObject("/Backend", self._backend_adaptor, QDBusConnection.ExportAllContents)


class _ApplicationAdaptor(QDBusAbstractAdaptor):
    Q_CLASSINFO("D-Bus Interface", "nl.ultimaker.cura.Application")

    def __init__(self, parent = None):
        super().__init__(parent)
        self._session_bus = QDBusConnection.sessionBus()

    @pyqtSlot(QDBusMessage)
    def openFile(self, message: QDBusMessage):
        if len(message.arguments()) != 1:
            return
        file_path = message.arguments()[0]
        Application.getInstance().readLocalFile(QUrl.fromLocalFile(file_path))

    @pyqtSlot()
    def quit(self):
        Application.getInstance().closeApplication()

    @pyqtSlot(QDBusMessage)
    def addMachine(self, message: QDBusMessage):
        definition_id, machine_name = message.arguments()[:2]
        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.addMachine(machine_name, definition_id)

    @pyqtSlot(QDBusMessage)
    def hasMachine(self, message: QDBusMessage):
        machine_name = message.arguments()[0]

        machine_manager = Application.getInstance().getMachineManager()
        result = machine_manager.hasMachine(machine_name)
        reply = message.createReply()
        reply.setArguments([result])
        self._session_bus.send(reply)

    @pyqtSlot(QDBusMessage)
    def renameMachine(self, message: QDBusMessage):
        old_machine_name, new_machine_name = message.arguments()[:2]
        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.renameMachine(old_machine_name, new_machine_name)

    @pyqtSlot(QDBusMessage)
    def removeMachine(self, message: QDBusMessage):
        machine_name = message.arguments()[0]

        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.removeMachine(machine_name)

    @pyqtSlot(QDBusMessage)
    def getActiveMachineName(self, message: QDBusMessage):
        global_stack = Application.getInstance().getGlobalContainerStack()
        reply = message.createReply()
        reply.setArguments([global_stack.getName()])
        self._session_bus.send(reply)

    @pyqtSlot(QDBusMessage)
    def setActiveMachine(self, message: QDBusMessage):
        machine_name = message.arguments()[0]

        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.setActiveMachine(machine_name)

    @pyqtSlot(QDBusMessage)
    def setActiveMaterial(self, message: QDBusMessage):
        material_id = message.arguments()[0]

        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.setActiveMaterial(material_id)

    @pyqtSlot(QDBusMessage)
    def getActiveMaterial(self, message: QDBusMessage):
        machine_manager = Application.getInstance().getMachineManager()

        reply = message.createReply()
        reply.setArguments([machine_manager.getActiveMaterial().serializeMetaData()])
        self._session_bus.send(reply)

    @pyqtSlot(QDBusMessage)
    def createMaterial(self, message: QDBusMessage):
        from cura.Settings.ContainerManager import ContainerManager
        container_manager = ContainerManager.getInstance()

        new_id = message.arguments()[0]
        new_name = message.arguments()[1]

        container_manager.createMaterial(new_id = new_id, new_name = new_name)

    @pyqtSlot(QDBusMessage)
    def duplicateMaterial(self, message: QDBusMessage):
        from cura.Settings.ContainerManager import ContainerManager
        container_manager = ContainerManager.getInstance()

        base_material_id = message.arguments()[0]  # material to duplicate from
        new_id = message.arguments()[1]  # (preferred) duplicated material ID

        container_manager.duplicateMaterial(base_material_id, new_id)

    @pyqtSlot(QDBusMessage)
    def hasMaterial(self, message: QDBusMessage):
        machine_manager = Application.getInstance().getMachineManager()

        material_id = message.arguments()[0]

        reply = message.createReply()
        reply.setArguments([machine_manager.hasMaterial(material_id)])
        self._session_bus.send(reply)

    @pyqtSlot(QDBusMessage)
    def getMaterial(self, message: QDBusMessage):
        from UM.Settings.ContainerRegistry import ContainerRegistry
        container_registry = ContainerRegistry.getInstance()

        material_id = message.arguments()[0]

        material = container_registry.findInstanceContainers(id = material_id, type = "material")
        material_data = None
        if material:
            material = material[0]
            material_data = material.serializeMetaData()

        reply = message.createReply()
        reply.setArguments([material_data])
        self._session_bus.send(reply)

    @pyqtSlot(QDBusMessage)
    def renameMaterial(self, message: QDBusMessage):
        machine_manager = Application.getInstance().getMachineManager()

        material_id = message.arguments()[0]
        new_material_name = message.arguments()[1]

        machine_manager.renameMaterial(material_id, new_material_name)

    @pyqtSlot(QDBusMessage)
    def removeMaterial(self, message: QDBusMessage):
        machine_manager = Application.getInstance().getMachineManager()

        material_id = message.arguments()[0]

        machine_manager.removeMaterial(material_id)

    @pyqtSlot(QDBusMessage)
    def saveFile(self, message: QDBusMessage):
        if not message.arguments() or len(message.arguments()) > 2:
            return
        file_path = message.arguments()[0]
        mime_type = "text/x-gcode"
        if len(message.arguments()) == 2:
            mime_type = message.arguments()[1]

        nodes = Application.getInstance().getController().getScene().getRoot()
        output_device = Application.getInstance().getOutputDeviceManager().getOutputDevice("local_file")
        output_device.requestWrite(nodes, file_path, [mime_type], None, silent = True, preferred_mimetype = mime_type)

    @pyqtProperty(str)
    def getVersion(self):
        return Application.getInstance().getVersion()

    @pyqtSlot(QDBusMessage)
    def setQualityProfile(self, message: QDBusMessage):
        qualityProfileName = message.arguments()[0]

        machine_manager = Application.getInstance().getMachineManager()
        machine_manager.setActiveQuality(qualityProfileName)

    @pyqtSlot(QDBusMessage)
    def getQualityProfiles(self, message: QDBusMessage):
        available_quality_profiles = ProfilesModel.getInstance().items
        qualities = []
        for quality_profile in available_quality_profiles:
            qualities.append({
                "name":quality_profile["name"],
                "id": quality_profile["id"]
            })

        reply = message.createReply()
        reply.setArguments(qualities)
        self._session_bus.send(reply)

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
