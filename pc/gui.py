import sys
import time

from PyQt6.QtCore import QTimer, pyqtSignal, QThread

from scenarios import get_scenario_targets
from simulator import update_sensor_values
from serial_manager import SerialManager
from graph_manager import GraphManager
from data_logger import DataLogger
from serial_worker import SerialWorker

from PyQt6.QtWidgets import(
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QScrollArea,
    QGroupBox,
    QHBoxLayout
)

#handling the window close event
class SensorSimulationWindow(QWidget):
    send_serial_command = pyqtSignal(str)
    disconnect_serial = pyqtSignal()
    def closeEvent(self, event):
        global logging_active, closing_app
        timer.stop()

        if logging_active:
            data_logger.stop_logging()
            logging_active = False

        if serial_manager.is_connected() and not closing_app:

            closing_app = True
            window.disconnect_serial.emit()
            event.ignore() #dont close the window yet.
            return

            
        #serial work finished, so stop the worker thread
        serial_thread.quit()
        serial_thread.wait()

        event.accept()

#define the whole window and added features along with some default values.
app = QApplication(sys.argv)
window = SensorSimulationWindow()

window.setWindowTitle("Sensor Simulator")
window.resize(1200,800)

title = QLabel("MCU Sensor Simulation Dashboard")

temperature_label = QLabel("Temperature: -- °C")
light_label = QLabel("Light Level: --")
humidity_label = QLabel("Humidity Level: -- %")
connection_label = QLabel("Arduino: Disconnected")
system_state_label = QLabel("System State: --")
scenario_status_label = QLabel("Scenario Status --")
fault_status_label = QLabel("Fault Status: None")
logging_status_label = QLabel("Logging Status: Off")
logging_file_label = QLabel("File: --")

connect_button =  QPushButton("Connect Arduino")
disconnect_button = QPushButton("Disconnect Arduino")
start_button = QPushButton("Start Simulation")
stop_button = QPushButton("Stop Simulation")
reset_button = QPushButton("Reset Simulation")
run_scenario_button = QPushButton("Run Scenario")
start_logging_button = QPushButton("Start Logging")
stop_logging_button = QPushButton("Stop Logging")

#managers
graph_manager = GraphManager()
data_logger = DataLogger()

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

#creating the serial manager and worker
serial_manager = SerialManager() 
serial_worker = SerialWorker(serial_manager)
serial_thread = QThread() #create the thread
serial_worker.moveToThread(serial_thread) #move the slot functions of serial_worker to serial_thread
serial_thread.start()


#initialized default values
temperature = 22.0
light = 700
humidity = 50.0
current_system_state = "Unknown"
current_fault = "None"
active_scenario = None
scenario_start_time = None
fault_latched = False
logging_active = False
start_time = None
reset_elapsed_time = None
closing_app = False
saved_target_temp = "25"
saved_target_light = "400"
saved_target_humidity = "50"

#connecting the arduino
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

#disconnecting the arduino
def disconnect_arduino():
    window.disconnect_serial.emit()

#for starting the automatic simulation whether sceanrio or user defined targets.
def start_simulation(from_scenario=False):
    global start_time, active_scenario, scenario_start_time

    if mode_box.currentText() == "Automatic":
        if not from_scenario:
            try:
                float(target_temp_input.text())
                float(target_light_input.text())
                float(target_humidity_input.text())
            except ValueError:
                print("Invalid target input")
                return

            active_scenario = None
            scenario_start_time = None

        start_time = time.time()

        graph_manager.reset()

        interval_map = {"0.25s":250,
                        "0.5s":500,
                        "1.0s":1000,
                        "2.0s":2000}
        interval = interval_map[speed_box.currentText()]

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

#handling the switch between automatic and manual modes
def mode_changed():
    if mode_box.currentText() == "Manual":
        timer.stop()
    update_ui_state()

#send the sensor values to the arduino    
def send_to_arduino(sensor, value):

    if not serial_manager.is_connected():
        return

    message = f"{sensor}:{value}"
    window.send_serial_command.emit(message)
        
#dealing with the manual values (updating the labels, graph, and sending to arduino)
def send_manual_values():
    global start_time, logging_active, current_system_state, current_fault

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

        if logging_active:
            current_time = time.time() - start_time
            data_logger.log_reading(current_time, temp_value, light_value, humidity_value,
                                    current_system_state, "None", current_fault)


    except ValueError:
        print("Invalid manual input")

#updating the graphs
def update_graphs(temp_value, light_value, humidity_value):
    global start_time
    current_time = time.time() - start_time
    graph_manager.add_reading(current_time, temp_value, light_value, humidity_value)
    
#dealing with updating the sensors for automatic.
def update_sensors():
    global temperature, light, humidity, logging_active
    global current_system_state, active_scenario, start_time, current_fault
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

    if logging_active:
        current_time = time.time() - start_time

        data_logger.log_reading(current_time, temperature, light, humidity, 
                                current_system_state, 
                                active_scenario if active_scenario is not None else "None",
                                current_fault)

#showing the available arduino ports.
def refresh_ports():
    port_box.clear()

    ports = serial_manager.get_ports()

    for port in ports:
        port_box.addItem(f"{port.device} - {port.description}", port.device)

    if port_box.count() == 0:
        port_box.addItem("No serial devices found", None)

#update the ui features based on the current state of the simulator.
def update_ui_state():
    global fault_latched, logging_active
    connected = serial_manager.is_connected()
    automatic = mode_box.currentText() == "Automatic"
    running = timer.isActive()

    connect_button.setEnabled(not connected)
    disconnect_button.setEnabled(connected and not running)

    port_box.setEnabled(not connected)
    refresh_ports_button.setEnabled(not connected)
    mode_box.setEnabled(not running)

    start_button.setEnabled(connected and automatic and not running and not fault_latched)
    stop_button.setEnabled(connected and automatic and running)
    manual_temp_input.setEnabled(connected and not automatic)
    manual_light_input.setEnabled(connected and not automatic)
    manual_humidity_input.setEnabled(connected and not automatic)
    send_manual_button.setEnabled(connected and not automatic and not fault_latched)
    reset_button.setEnabled(connected)
    start_logging_button.setEnabled(connected and not logging_active)
    stop_logging_button.setEnabled(logging_active)

    scenario_box.setEnabled(connected and automatic and not running)
    run_scenario_button.setEnabled(connected and automatic and not running and not fault_latched)
    target_temp_input.setEnabled(connected and automatic and not running)
    target_light_input.setEnabled(connected and automatic and not running)
    target_humidity_input.setEnabled(connected and automatic and not running)
    speed_box.setEnabled(connected and automatic and not running)

    fault_box.setEnabled(connected)
    inject_fault_button.setEnabled(connected and not fault_latched)

#resetting the simulation
def reset_simulation():
    global temperature,light,humidity,start_time,fault_latched
    global current_fault,current_system_state,reset_elapsed_time,active_scenario,scenario_start_time
    global saved_target_humidity, saved_target_light, saved_target_temp

    timer.stop()

    if serial_manager.is_connected():
        window.send_serial_command.emit("RESET")

    #store the relapsed time
    if start_time is not None:
        reset_elapsed_time = time.time() - start_time
    else:
        reset_elapsed_time = None
    
    temperature = 22.0
    light = 700
    humidity = 50.0
    start_time = None
    current_system_state = "NORMAL"
    current_fault = "None"
    active_scenario = None
    scenario_start_time = None
    fault_latched = False

    temperature_label.setText("Temperature: -- °C")
    light_label.setText("Light Level: --")
    humidity_label.setText("Humidity: -- %")
    system_state_label.setText("System State: Normal")
    scenario_status_label.setText("Scenario Status --")

    target_temp_input.setText(saved_target_temp)
    target_light_input.setText(saved_target_light)
    target_humidity_input.setText(saved_target_humidity)

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

#handle scenario completion.
def finish_scenario():
    global active_scenario, scenario_start_time
    timer.stop()

    if serial_manager.is_connected():
        window.send_serial_command.emit("RESET")

    active_scenario = None
    scenario_start_time = None

    target_temp_input.setText(saved_target_temp)
    target_light_input.setText(saved_target_light)
    target_humidity_input.setText(saved_target_humidity)

    scenario_status_label.setText("Scenario Status: Complete")

    update_ui_state()

#fault injection
def inject_fault():
    
    fault_type = fault_box.currentText()

    if (fault_type == "Invalid Temperature"):
        command = "TEMP:abc"

    elif (fault_type == "Out-of-Range Temperature"):
        command = "TEMP:999"

    elif (fault_type == "Invalid Light"):
        command = "LIGHT:abc"

    elif (fault_type == "Out-of-Range Light"):
        command = "LIGHT:-50"

    elif (fault_type == "Invalid Humidity"):
        command = "HUMIDITY:abc"

    else:
        command = "HUMIDITY:150"

    window.send_serial_command.emit(command)

#handle the arduino responses on Python.
def handle_arduino_response(response):
    global fault_latched, current_system_state
    global current_fault, logging_active, temperature, light, humidity 
    global start_time, active_scenario, reset_elapsed_time
    if response is None:
        return

    print("Arduino:", response)

    if response.startswith("STATE:"):
        state = response.split(":", 1)[1].strip()
        current_system_state = state

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
        current_system_state = "FAULT"
        current_fault = fault

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

        if (logging_active and start_time is not None):
            current_time = time.time() - start_time
            data_logger.log_reading(current_time,temperature,light,humidity,current_system_state,
                                    active_scenario if active_scenario is not None else "None",
                                    current_fault)

        timer.stop()
        update_ui_state()

    elif (response == "System Reset"):

        fault_latched = False
        current_system_state = "NORMAL"
        current_fault = "None"

        fault_status_label.setText("Fault Status: None")

        if (logging_active and reset_elapsed_time is not None):
            data_logger.log_reading(reset_elapsed_time,
            temperature, light, humidity, current_system_state,
            active_scenario if active_scenario is not None else "None",
            "RESET")

        reset_elapsed_time = None

        update_ui_state()

#start the logging
def start_logging():
    global logging_active

    data_logger.start_logging()
    logging_active = True

    print("Logging started:", data_logger.file_path)
    logging_status_label.setText("Logging Status: ON")
    logging_file_label.setText(f"File: {data_logger.file_path}")

    update_ui_state()

#stop the logging
def stop_logging():
    global logging_active

    data_logger.stop_logging()
    logging_active = False

    print("Logging stopped")
    logging_status_label.setText("Logging Status: OFF")
    logging_file_label.setText(f"File: --")

    update_ui_state()

#handling when disconnect is finished
def handle_disconnect_finished(response):
    global closing_app
    print("Arduino:", response)
    connection_label.setText("Arduino: Disconnected")

    if closing_app:
        serial_thread.quit()
        serial_thread.wait()

        window.close()
        return

    update_ui_state()

#handling error occurence (ex. arduino disconnected mid run)
def handle_error_occured(error):
    print("Serial error:", error)
    timer.stop()

    serial_manager.close_connection()
    connection_label.setText("Arduino: Connection Lost")
    update_ui_state()

#setting the layout
content_widget = QWidget()
layout = QVBoxLayout(content_widget)

scroll_area = QScrollArea()
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(content_widget)

layout.addWidget(title)
title.setStyleSheet("font-size: 22px; font-weight: bold;")

#Connection Group
connection_group = QGroupBox("Connection")
connection_layout = QVBoxLayout()
connection_button_layout = QHBoxLayout()

connection_layout.addWidget(connection_label)
connection_layout.addWidget(QLabel("Arduino Port:"))
connection_layout.addWidget(port_box)

connection_button_layout.addWidget(connect_button)
connection_button_layout.addWidget(disconnect_button)
connection_layout.addWidget(refresh_ports_button)
connection_layout.addLayout(connection_button_layout)

connection_group.setLayout(connection_layout)


# Simulation group
simulation_group = QGroupBox("Simulation")
simulation_layout = QVBoxLayout()

simulation_layout.addWidget(QLabel("Mode:"))
simulation_layout.addWidget(mode_box)

simulation_layout.addWidget(QLabel("Update Rate:"))
simulation_layout.addWidget(speed_box)

simulation_layout.addWidget(reset_button)

simulation_group.setLayout(simulation_layout)

#Target Group
target_group = QGroupBox("Target Settings")
target_layout = QVBoxLayout()

target_layout.addWidget(QLabel("Target Temperature:"))
target_layout.addWidget(target_temp_input)

target_layout.addWidget(QLabel("Target Light Level:"))
target_layout.addWidget(target_light_input)

target_layout.addWidget(QLabel("Target Humidity:"))
target_layout.addWidget(target_humidity_input)

target_group.setLayout(target_layout)

#Scenario group
scenario_group = QGroupBox("Scenario Settings")
scenario_layout = QVBoxLayout()

scenario_layout.addWidget(scenario_box)
scenario_layout.addWidget(run_scenario_button)
scenario_layout.addWidget(scenario_status_label)

scenario_group.setLayout(scenario_layout)

# Fault injection group
fault_group = QGroupBox("Fault Injection")
fault_layout = QVBoxLayout()

fault_layout.addWidget(fault_box)
fault_layout.addWidget(inject_fault_button)
fault_layout.addWidget(fault_status_label)

fault_group.setLayout(fault_layout)

#manual group
manual_group = QGroupBox("Manual Settings")
manual_layout = QVBoxLayout()

manual_layout.addWidget(manual_temp_input)
manual_layout.addWidget(manual_light_input)
manual_layout.addWidget(manual_humidity_input)
manual_layout.addWidget(send_manual_button)

manual_group.setLayout(manual_layout)

# System status group
status_group = QGroupBox("System Status")
status_layout = QVBoxLayout()

sensor_status_layout = QHBoxLayout()

sensor_status_layout.addWidget(temperature_label)
sensor_status_layout.addWidget(light_label)
sensor_status_layout.addWidget(humidity_label)

status_layout.addLayout(sensor_status_layout)
system_state_label.setStyleSheet("font-weight: bold; font-size: 14px;")
status_layout.addWidget(system_state_label)


status_group.setLayout(status_layout)

# Data logging group
logging_group = QGroupBox("Data Logging")
logging_layout = QVBoxLayout()

logging_layout.addWidget(logging_status_label)
logging_layout.addWidget(logging_file_label)
logging_layout.addWidget(start_logging_button)
logging_layout.addWidget(stop_logging_button)

logging_group.setLayout(logging_layout)

left_layout = QVBoxLayout()

#setting up the entire layout properly
left_layout.addWidget(connection_group)
left_layout.addWidget(simulation_group)
left_layout.addWidget(target_group)
left_layout.addWidget(manual_group)
left_layout.addWidget(scenario_group)
left_layout.addWidget(fault_group)
left_layout.addWidget(logging_group)

left_layout.addStretch()

right_layout = QVBoxLayout()

right_layout.addWidget(status_group)
right_layout.addWidget(graph_manager.canvas, stretch=1)

simulation_button_layout = QHBoxLayout()

simulation_button_layout.addWidget(start_button)
simulation_button_layout.addWidget(stop_button)

right_layout.addLayout(simulation_button_layout)

dashboard_layout = QHBoxLayout()
dashboard_layout.addLayout(left_layout, 1)
dashboard_layout.addLayout(right_layout, 2) #graphs get 2x horizontal space

dashboard_layout.setSpacing(15)
layout.setContentsMargins(15, 15, 15, 15)
layout.setSpacing(10)

control_groups = [
    connection_group,
    simulation_group,
    target_group,
    manual_group,
    scenario_group,
    fault_group,
    logging_group
]

for group in control_groups:
    group.setMaximumWidth(500)

layout.addLayout(dashboard_layout)


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
start_logging_button.clicked.connect(start_logging)
stop_logging_button.clicked.connect(stop_logging)
window.send_serial_command.connect(serial_worker.send_command)
window.disconnect_serial.connect(serial_worker.disconnect)
serial_worker.response_received.connect(handle_arduino_response)
serial_worker.disconnect_finished.connect(handle_disconnect_finished)
serial_worker.error_occured.connect(handle_error_occured)

refresh_ports()
update_ui_state()

window.show()

sys.exit(app.exec())