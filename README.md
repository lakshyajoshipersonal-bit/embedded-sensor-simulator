#MCU Sensor Simulation Dashboard
A desktop based sensor simulation and monitoring system that integrates a Python PyQt6 GUI with an arduino over serial communication.

The application simulates temperature, light, and humidity sensor data in real time allowing users to run predefined environmental scenarios, automatic simulations, manually control sensor data, inject sensor faults, visualize sensor data through graphs, and record simulation results to CSV files.

Serial communication is handled asynchronously using a worker thread, allowing the GUI to remain responsive during communication and connection failures.

##Features
1. Real-time temperature, light, and humidity sensor simulation
2. Automatic and manual simulation modes
3. Configurable sensor target values and simulation update rates
4. Predefined environmental scenarios
5. Sensor fault injection and fault recovery
6. Real-time sensor graphs using Matplotlib
7. CSV data logging with system state, scenario, and fault information
8. Using PyQt threads for asynchronous arduino serial communication
9. Automatic detection and handling of unexpected Arduino disconnections
10. Arduino-controlled system states and LED behavior

##Dashboard
![MCU Sensor Simulation Dashboard](pc/assets/dark_scenario.png)
The dashboard provides visual monitoring in the form of graphs, and status labels while communicating with the 
arduino over serial during any kind of simulation run.

##Scenario Simulation
![Dark Scenario Simulation](pc/assets/dashboard.png)

Predefined scenarios progressively modify environmental conditions over multiple
stages. The example above shows the Dark scenario reducing the simulated light
level toward and below the configured dark threshold.

