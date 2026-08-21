from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class SerialWorker(QObject):
    response_received = pyqtSignal(str)
    disconnect_finished = pyqtSignal(str)

    def __init__(self, serial_manager):
        super().__init__()
        self.serial_manager = serial_manager

    @pyqtSlot(str)
    def send_command(self, command):
        response = self.serial_manager.send_command(command)

        if response is not None:
            self.response_received.emit(response)

    @pyqtSlot()
    def disconnect(self):
        response = self.serial_manager.disconnect()
        self.disconnect_finished.emit(response)
        
    



