from data_logger import DataLogger
import os
import csv

logger = DataLogger()
def test_start_logging_createsFiles(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path) #temporarily changes the current working directory
    #with the created temporary directory
    logger.start_logging()

    assert os.path.exists(logger.file_path)

    logger.stop_logging()

    with open(logger.file_path, "r", newline = "") as file:
        reader = csv.reader(file)
        rows = list(reader)

    assert rows[0] == [
            "Timestamp",
            "Elapsed Time",
            "Temperature",
            "Light",
            "Humidity",
            "System State",
            "Scenario",
            "Fault"
        ]

def test_log_reading(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    logger.start_logging()
    
    logger.log_reading(elapsed_time=5.25, temperature=32.5,
                       light=700, humidity=50, system_state="OVERHEAT",
                       scenario="None", fault="None")

    logger.stop_logging()

    with open(logger.file_path, "r", newline = "") as file:
        reader = csv.reader(file)
        rows = list(reader)


    result = rows[1]

    assert result[1] == "5.25" 
    assert result[2] == "32.5"
    assert result[3] == "700"
    assert result[4] == "50"
    assert result[5] == "OVERHEAT"
    assert result[6] == "None"
    assert result[7] == "None"

