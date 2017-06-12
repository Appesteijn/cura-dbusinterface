import sys
import time
import os
import os.path

from PyQt5.QtCore import QProcess, QTimer, QProcessEnvironment
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtDBus import QDBusConnection, QDBusMessage

app = QGuiApplication(sys.argv)

cura_process = None

def call_cura(method, *args):
    dbus_service = "nl.ultimaker.cura"
    dbus_object = "/Application"
    dbus_interface = "nl.ultimaker.cura.Application"

    message = QDBusMessage.createMethodCall(dbus_service, dbus_object, dbus_interface, method)
    message.setArguments(args)
    QDBusConnection.sessionBus().call(message)

def start_cura():
    global cura_process
    cura_process = QProcess()
    env = QProcessEnvironment.systemEnvironment()
    env.insert("PYTHONPATH", "/home/ahiemstra/dev/master/inst/lib/python3/dist-packages/")
    cura_process.setProcessEnvironment(env)

    cura_process.start("/usr/bin/python", ["/home/ahiemstra/dev/master/inst/bin/cura"])
    cura_process.waitForStarted()

    time.sleep(30)

def stop_cura():
    call_cura("quit")

    cura_process.waitForFinished()

def test():
    print("Starting Test...")

    start_cura()

    file_path = "/home/ahiemstra/Downloads/test.gcode"
    file_path_no_ext = "/home/ahiemstra/Downloads/test"

    call_cura("openFile", "/home/ahiemstra/Downloads/SKULL1.STL")

    time.sleep(60)

    if(os.path.exists(file_path)):
        os.remove(file_path)

    call_cura("saveFile", file_path_no_ext, "text/x-gcode")

    time.sleep(5)

    assert os.path.exists(file_path)

    with open(file_path) as f:
        line = f.readline().strip()
        assert line == ";FLAVOR:UltiGCode"

    stop_cura()

    print("Test Successful!")

    app.quit()



timer = QTimer()
timer.timeout.connect(test)
timer.start()

app.exec_()
