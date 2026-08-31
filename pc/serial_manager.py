import serial
from serial.tools import list_ports

class SerialManager():
    def __init__(self):
        self.arduino = None

    def get_ports(self):
        return list_ports.comports()

    def connect(self, port, baud_rate = 9600):
        self.arduino = serial.Serial(port, baud_rate, timeout=1)

    def disconnect(self):
        if self.arduino is None:
            return None

        self.arduino.write("QUIT".encode())
        response = self.arduino.readline().decode().strip()

        
        self.arduino.close()
        self.arduino = None

        if response == "":
            return "Disconnected"

        return response

    def is_connected(self):
        return self.arduino is not None and self.arduino.is_open

    def send_command(self, command):
        if self.arduino is None:
            return None

        self.arduino.write(f"{command}\n".encode())
        response = self.arduino.readline().decode().strip()

        return response

    def close_connection(self):
        if self.arduino is not None:
            try:
                self.arduino.close()
            except serial.SerialException:
                pass
            self.arduino = None

    
        
