import csv
from signal_writer_interface import SignalWriter
import os

class CSVSignalWriter(SignalWriter):
    def __init__(self, file_path):
        self.file_path = file_path
    def write(self, signals):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["symbol", "timestamp_IST", "action", "price", "status"])
        with open(self.file_path, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["symbol", "timestamp_IST", "action", "price", "status"])
            writer.writeheader()
            writer.writerows(signals)
