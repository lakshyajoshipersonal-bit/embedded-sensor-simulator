import csv
import os
from datetime import datetime

#for data logging in a csv file.
class DataLogger:
    def __init__(self):
        self.file = None
        self.writer = None
        self.file_path = None

    def start_logging(self):
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.file_path = f"logs/run_{timestamp}.csv"
        self.file = open(self.file_path, "w", newline="")

        self.writer = csv.writer(self.file)
        self.writer.writerow([
            "Timestamp",
            "Elapsed Time",
            "Temperature",
            "Light",
            "Humidity",
            "System State",
            "Scenario",
            "Fault"
        ])

    def log_reading(self, elapsed_time, temperature,
                    light, humidity, system_state, scenario, fault):

        if self.writer is None:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        self.writer.writerow([
                    timestamp,
                    round(elapsed_time,2),
                    round(temperature,2),
                    light,
                    round(humidity,2),
                    system_state,
                    scenario,
                    fault
                ])
        self.file.flush()

    def stop_logging(self):
        if self.file is not None:
            self.file.close()

        self.file = None
        self.writer = None



