import serial
import pytest
from unittest.mock import MagicMock, patch
from serial_manager import SerialManager

def test_send_command():
    serial_manager = SerialManager()
    fake_arduino = MagicMock()

    #return "STATE:NORMAL" whenever readline() is called
    fake_arduino.readline.return_value = b"STATE: NORMAL\n"

    serial_manager.arduino = fake_arduino

    response = serial_manager.send_command("SENSORS:25.0,700,50.0")

    #verify write was called exactly once with the given argument
    fake_arduino.write.assert_called_once_with(
        b"SENSORS:25.0,700,50.0\n"
    )

    assert response == "STATE: NORMAL"


def test_send_command_when_disconnected():
    serial_manager = SerialManager()

    response = serial_manager.send_command("SENSORS:25.0,700,50.0")

    assert response is None

def test_connect():
    serial_manager = SerialManager()

    with patch("serial_manager.serial.Serial") as mock_serial: #temporarily replace serial.Serial
        #with mock_serial, and automatically restore it after
        fake_arduino = MagicMock()
        mock_serial.return_value = fake_arduino #causes serial.Serial to return fake_arduino

        serial_manager.connect("COM3")

        #verify mock_serial was called exactly once with the given arguments.
        mock_serial.assert_called_once_with(
            "COM3", 9600, timeout=1
        )

        assert serial_manager.arduino == fake_arduino #check if connect successful

def test_disconnect():
    serial_manager = SerialManager()
    fake_arduino = MagicMock()

    fake_arduino.readline.return_value = b"Quitting sensor\n"

    serial_manager.arduino = fake_arduino

    response = serial_manager.disconnect()

    fake_arduino.write.assert_called_once_with(b"QUIT")

    assert serial_manager.arduino is None
    assert response == "Quitting sensor"

def test_is_connected():
    serial_manager = SerialManager()

    #no arduino connected
    assert serial_manager.is_connected() is False

    #fake connected arduino
    fake_arduino = MagicMock()
    fake_arduino.is_open = True

    serial_manager.arduino = fake_arduino
    assert serial_manager.is_connected() is True

    #fake arduino exists but port is closed
    fake_arduino.is_open = False
    assert serial_manager.is_connected() is False


def test_connect_failure():
    serial_manager = SerialManager()

    with patch("serial_manager.serial.Serial") as mock_serial:
        mock_serial.side_effect = serial.SerialException("Could not open port") #causes serial.Serial to 
        #raise this exception

        #expect the code inside the block to raise serial.SerialException.
        with pytest.raises(serial.SerialException): 
            serial_manager.connect("COM3")

        assert serial_manager.arduino is None

