import sys
import serial
import time

from PyQt6.QtCore import QTimer


from scenarios import get_scenario_targets
from simulator import update_sensor_values
from serial_manager import SerialManager
from graph_manager import GraphManager


from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QScrollArea
)

#defining the window close event, particularly making sure that we disconnect the arduino.
class SensorSimulationWindow(QWidget):
    def closeEvent(self, event):
        timer.stop()

        if serial_manager.is_connected():
            try:
                response = serial_manager.disconnect()

                if response is not None:
                    print("Arduino:", response)

            except serial.SerialException:
                pass
        event.accept()

#define the whole window and added features along with some defaults.
app = QApplication(sys.argv)
window = SensorSimulationWindow()

window.setWindowTitle("Sensor Simulator")
window.resize(1200,800)

title = QLabel("Sensor Simulator")

temperature_label = QLabel("Temperature: -- °C")
light_label = QLabel("Light Level: --")
humidity_label = QLabel("Humidity Level: -- %")
connection_label = QLabel("Arduino: Disconnected")
system_state_label = QLabel("System State: --")
scenario_status_label = QLabel("Scenario Status --")
fault_status_label = QLabel("Fault Status: None")

connect_button =  QPushButton("Connect Arduino")
disconnect_button = QPushButton("Disconnect Arduino")
start_button = QPushButton("Start Simulation")
stop_button = QPushButton("Stop Simulation")
reset_button = QPushButton("Reset Simulation")
run_scenario_button = QPushButton("Run Scenario")

graph_manager = GraphManager()

mode_box = QComboBox()
mode_box.addItems(["Automatic", "Manual"])

port_box = QComboBox()
refresh_ports_button = QPushButton("Refresh Ports")

fault_box = QComboBox()
fault_box.addItems(["Invalid Temperature",
                    "Out-of-Range Temperature",
                    "Invalid Light",
                    "Out-of-Range Light",
                    "Invalid Humidity",
                    "Out-of-Range Humidity"
                  ])
inject_fault_button = QPushButton("Inject Fault")

speed_box = QComboBox()
speed_box.addItems(["0.25s", "0.5s", "1.0s", "2.0s"])
speed_box.setCurrentText("1.0s")

scenario_box = QComboBox()
scenario_box.addItems(["Normal Operation",
                       "Overheating",
                       "Dark",
                       "Overheat + Dark"])

manual_temp_input = QLineEdit()
manual_temp_input.setPlaceholderText("Enter Temperature: ")

manual_light_input = QLineEdit()
manual_light_input.setPlaceholderText("Enter Light Level: ")

manual_humidity_input = QLineEdit()
manual_humidity_input.setPlaceholderText("Enter Humidity Level: ")

send_manual_button = QPushButton("Send Manual Values")

target_temp_input = QLineEdit()
target_temp_input.setPlaceholderText("Target Temperature")

target_light_input = QLineEdit()
target_light_input.setPlaceholderText("Target Light")

target_humidity_input = QLineEdit()
target_humidity_input.setPlaceholderText("Target Humidity")

target_temp_input.setText("25")
target_light_input.setText("400")
target_humidity_input.setText("50")

start_time = None


#initialized values
temperature = 22.0
light = 700
humidity = 50.0
serial_manager = SerialManager() #default constructor in order to set the arduino up.
active_scenario = None
scenario_start_time = None
fault_latched = False

saved_target_temp = "25"
saved_target_light = "400"
saved_target_humidity = "50"

#target_humidity = 50.0

#connect the arduino
def connect_arduino():
    selected_port = port_box.currentData()

    if selected_port is None:
        connection_label.setText("Arduino: No port selected")
        return

    try:
        serial_manager.connect(selected_port)

        connection_label.setText(f"Arduino: Connected ({selected_port})")
        print("Arduino connected on ", selected_port)
        update_ui_state()

    except Exception as e:
        connection_label.setText("Arduino: Connection Failed")
        print("Connection failed:", e)

#disconnect the arduino
def disconnect_arduino():
    try:
        response = serial_manager.disconnect()
        if response is not None:
            print("Arduino:", response)

    except serial.SerialException as e:
        print("Disconnect failed:", e)

    connection_label.setText("Arduino: Disconnected")
    update_ui_state()
    

#for starting the automatic simulation whether sceanrio or user defined targets.
def start_simulation(from_scenario=False):
    global start_time, active_scenario, scenario_start_time

    if mode_box.currentText() == "Automatic":
        if not from_scenario:
            active_scenario = None
            scenario_start_time = None

        start_time = time.time()

        graph_manager.reset()

        selected_speed = speed_box.currentText()

        if(selected_speed == "0.25s"):
            interval = 250
        elif (selected_speed == "0.5s"):
            interval = 500
        elif (selected_speed == "1.0s"):
            interval = 1000
        else:
            interval = 2000


        timer.start(interval)
        update_ui_state()

#stopping the automatic simulation
def stop_simulation():
    global active_scenario, scenario_start_time

    timer.stop()

    if active_scenario is not None:
        active_scenario = None
        scenario_start_time = None

        target_temp_input.setText(saved_target_temp)
        target_light_input.setText(saved_target_light)
        target_humidity_input.setText(saved_target_humidity)
        


    update_ui_state()

#dealing with the case of changed mode from automatic to manual
def mode_changed():
    if mode_box.currentText() == "Manual":
        timer.stop()
    update_ui_state()

#send the sensor values to the arduino    
def send_to_arduino(sensor, value):

    if not serial_manager.is_connected():
        return

    try:
        message = f"{sensor}:{value}"

        response = serial_manager.send_command(message)

        handle_arduino_response(response)

    except serial.SerialException as e:
        print("Arduino connection lost:", e)

        timer.stop()

        connection_label.setText("Arduino: Connection Lost")

        update_ui_state()


#dealing with the manual values (updating the labels, graph, and sending to arduino)
def send_manual_values():
    global start_time

    if mode_box.currentText() != "Manual":
        return

    if start_time is None:
        start_time = time.time()

    try:
        temp_value = float(manual_temp_input.text())
        light_value = int(manual_light_input.text())
        humidity_value = float(manual_humidity_input.text())

        temperature_label.setText(
            f"Temperature: {temp_value:.1f} °C"
        )

        light_label.setText(
            f"Light Level: {light_value}"
        )

        humidity_label.setText(
                    f"Humidity: {humidity_value:.1f} %"
                )

        send_to_arduino("TEMP", f"{temp_value:.1f}")
        send_to_arduino("LIGHT", light_value)
        send_to_arduino("HUMIDITY", f"{humidity_value:.1f}")

        update_graphs(temp_value, light_value, humidity_value)

    except ValueError:
        print("Invalid manual input")

#updating the graphs, we only show the last 30 seconds history
def update_graphs(temp_value, light_value, humidity_value):
    current_time = time.time() - start_time
    graph_manager.add_reading(current_time, temp_value, light_value, humidity_value)
    
#dealing with updating the sensors for automatic.
def update_sensors():
    global temperature, light, humidity
    scenario_targets = get_current_scenario_targets()

    if scenario_targets == "FINISHED":
        return

    if scenario_targets is not None:
        target_temperature, target_light, target_humidity = scenario_targets
        

    else:
        try:
            target_temperature = float(target_temp_input.text())
            target_light = float(target_light_input.text())
            target_humidity = float(target_humidity_input.text())
        except ValueError:
            return

    temperature, light, humidity = update_sensor_values(temperature,light,humidity,
                                                        target_temperature,target_light,target_humidity)

    temperature_label.setText(f"Temperature: {temperature:.1f}°C")
    light_label.setText(f"Light Level: {light}")
    humidity_label.setText(f"Humidity: {humidity:.1f}%")

    send_to_arduino("TEMP", f"{temperature:.1f}")
    send_to_arduino("LIGHT", light)
    send_to_arduino("HUMIDITY", f"{humidity:.1f}")


    update_graphs(temperature, light, humidity)

#showing the available arduino ports.
def refresh_ports():
    port_box.clear()

    ports = serial_manager.get_ports()

    for port in ports:
        port_box.addItem(f"{port.device} - {port.description}", port.device)

    if port_box.count() == 0:
        port_box.addItem("No serial devices found", None)

#update the button display and other features based on the current mode.
def update_ui_state():
    connected = serial_manager.is_connected()
    automatic = mode_box.currentText() == "Automatic"
    running = timer.isActive()
    scenario_running = running and active_scenario is not None

    connect_button.setEnabled(not connected)
    disconnect_button.setEnabled(connected and not running)

    port_box.setEnabled(not connected)
    refresh_ports_button.setEnabled(not connected)

    start_button.setEnabled(connected and automatic and not running and not fault_latched)
    stop_button.setEnabled(connected and automatic and running)
    manual_temp_input.setEnabled(connected and not automatic)
    manual_light_input.setEnabled(connected and not automatic)
    manual_humidity_input.setEnabled(connected and not automatic)
    send_manual_button.setEnabled(connected and not automatic and not fault_latched)
    reset_button.setEnabled(connected)

    scenario_box.setEnabled(connected and automatic and not running)
    run_scenario_button.setEnabled(connected and automatic and not running and not fault_latched)
    target_temp_input.setEnabled(connected and automatic and not running and not scenario_running)
    target_light_input.setEnabled(connected and automatic and not running and not scenario_running)
    target_humidity_input.setEnabled(connected and automatic and not running and not scenario_running)
    speed_box.setEnabled(connected and automatic and not running)

    fault_box.setEnabled(connected)
    inject_fault_button.setEnabled(connected and not fault_latched)

#resetting the simulation
def reset_simulation():
    global temperature,light,start_time,fault_latched

    timer.stop()

    if serial_manager.is_connected():
        try:
            response = serial_manager.send_command("RESET")

            if response is not None:
                print("Arduino:", response)

            if response == "System Reset":
                fault_latched = False
                fault_status_label.setText("Fault Status: None")

           
        except serial.SerialException as e:
            print("Reset failed:", e)


    temperature = 22.0
    light = 700
    humidity = 50.0
    start_time = None

    temperature_label.setText("Temperature: -- °C")
    light_label.setText("Light Level: --")
    humidity_label.setText("Humidity: -- %")
    system_state_label.setText("System State: --")
    fault_status_label.setText("Fault Status: None")
    scenario_status_label.setText("Scenario Status --")

    fault_latched = False
    fault_status_label.setText("Fault Status: None")

    graph_manager.reset()

    update_ui_state()

#to run a particular scenario
def run_scenario():
    global active_scenario, scenario_start_time
    global saved_target_light, saved_target_temp, saved_target_humidity

    saved_target_temp = target_temp_input.text()
    saved_target_light = target_light_input.text()
    saved_target_humidity = target_humidity_input.text()

    active_scenario = scenario_box.currentText()
    scenario_start_time = time.time()

    


    target_temp_input.clear()
    target_light_input.clear()
    target_humidity_input.clear()
    start_simulation(True)

    QTimer.singleShot(
    0,
    lambda: scroll_area.ensureWidgetVisible(
        graph_manager.canvas
    )
)

#to get the scenario targets for particular scenarios
def get_current_scenario_targets():
    global scenario_start_time, active_scenario
    if active_scenario is None or scenario_start_time is None:
        return None
    scenario_time = time.time() - scenario_start_time

    if scenario_time < 5:
        stage = 1
    elif scenario_time < 10:
        stage = 2
    elif scenario_time < 15:
        stage = 3
    else:
        stage = 4

    scenario_status_label.setText(f"Scenario Status: {active_scenario} - Stage {stage}/4")

    if (scenario_time >= 30):
        finish_scenario()
        return "FINISHED"

    return get_scenario_targets(active_scenario, scenario_time)

#behavior on finishing the sceanrios.
def finish_scenario():
    global active_scenario, scenario_start_time
    timer.stop()

    if serial_manager.is_connected():
        try:
            response = serial_manager.send_command("RESET")

            

            if response is not None:
                print("Arduino:", response)

        except serial.SerialException as e:
            print("Scenario cleanup failed:", e)

    active_scenario = None
    scenario_start_time = None

    target_temp_input.setText(saved_target_temp)
    target_light_input.setText(saved_target_light)
    target_humidity_input.setText(saved_target_humidity)

    scenario_status_label.setText("Scenario Status: Complete")

    update_ui_state()

def inject_fault():
    
    fault_type = fault_box.currentText()

    if (fault_type == "Invalid Temperature"):
        response = serial_manager.send_command("TEMP:abc")

    elif (fault_type == "Out-of-Range Temperature"):
        response = serial_manager.send_command("TEMP:999")

    elif (fault_type == "Invalid Light"):
        response = serial_manager.send_command("LIGHT:abc")

    elif (fault_type == "Out-of-Range Light"):
        response = serial_manager.send_command("LIGHT:-50")

    elif (fault_type == "Invalid Humidity"):
        response = serial_manager.send_command("HUMIDITY:abc")

    else:
        response = serial_manager.send_command("HUMIDITY:150")
        

    handle_arduino_response(response)

def handle_arduino_response(response):
    global fault_latched
    if response is None:
        return

    print("Arduino:", response)

    if response.startswith("STATE:"):
        state = response.split(":", 1)[1].strip()

        system_state_label.setText(
            f"System State: {state}"
        )

        if state == "FAULT":
            fault_latched = True

            if fault_status_label.text() == "Fault Status: None":

                fault_status_label.setText(
                    "Fault Status: Fault detected - Reset required"
                )

            timer.stop()
            update_ui_state()

    elif response.startswith("FAULT:"):
        fault_latched = True
        fault = response.split(":", 1)[1].strip()

        system_state_label.setText("System State: FAULT")

        fault_messages = {
            "INVALID_TEMP": "Invalid temperature data",
            "TEMP_RANGE": "Temperature out of range",
            "INVALID_LIGHT": "Invalid light data",
            "LIGHT_RANGE": "Light level out of range",
            "INVALID_HUMIDITY": "Invalid humidity data",
            "HUMIDITY_RANGE": "Humidity out of range"
        }

        message = fault_messages.get(
            fault,
            "Unknown fault"
        )

        fault_status_label.setText(
            f"Fault Status: {message} - Reset required"
        )

        timer.stop()
        update_ui_state()




#setting the layout by adding the appropriate widgets in preferred sequence
content_widget = QWidget()
layout = QVBoxLayout(content_widget)

scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(content_widget)

layout.addWidget(title)

layout.addWidget(connection_label)

layout.addWidget(connect_button)
layout.addWidget(disconnect_button)

layout.addWidget(QLabel("Arduino Port:"))
layout.addWidget(port_box)
layout.addWidget(refresh_ports_button)

layout.addWidget(mode_box)

layout.addWidget(reset_button)

layout.addWidget(QLabel("Update Rate:"))
layout.addWidget(speed_box)

layout.addWidget(QLabel("Scenario:"))
layout.addWidget(scenario_box)
layout.addWidget(run_scenario_button)

layout.addWidget(QLabel("Fault Injection:"))
layout.addWidget(fault_box)
layout.addWidget(inject_fault_button)

layout.addWidget(QLabel("Target Temperature:"))
layout.addWidget(target_temp_input)
layout.addWidget(QLabel("Target Light Level:"))
layout.addWidget(target_light_input)
layout.addWidget(QLabel("Target Humidity:"))
layout.addWidget(target_humidity_input)

layout.addWidget(manual_temp_input)
layout.addWidget(manual_light_input)
layout.addWidget(manual_humidity_input)
layout.addWidget(send_manual_button)

layout.addWidget(temperature_label)

layout.addWidget(graph_manager.canvas, stretch=1)

layout.addWidget(light_label)
layout.addWidget(humidity_label)
layout.addWidget(system_state_label)
layout.addWidget(scenario_status_label)
layout.addWidget(fault_status_label)

layout.addWidget(start_button)
layout.addWidget(stop_button)

window_layout = QVBoxLayout(window)
window_layout.addWidget(scroll_area)

timer = QTimer()

timer.timeout.connect(update_sensors)

#definining the button behaviors.
start_button.clicked.connect(lambda: start_simulation(False))
stop_button.clicked.connect(stop_simulation)
connect_button.clicked.connect(connect_arduino)
disconnect_button.clicked.connect(disconnect_arduino)
send_manual_button.clicked.connect(send_manual_values)
mode_box.currentTextChanged.connect(mode_changed)
refresh_ports_button.clicked.connect(refresh_ports)
reset_button.clicked.connect(reset_simulation)
run_scenario_button.clicked.connect(run_scenario)
inject_fault_button.clicked.connect(inject_fault)

refresh_ports()
update_ui_state()


window.show()

sys.exit(app.exec())