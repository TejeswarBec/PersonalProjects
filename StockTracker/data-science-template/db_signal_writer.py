from signal_writer_interface import SignalWriter
import os
import sqlite3

class DBSignalWriter(SignalWriter):
    def __init__(self, db_path):
        self.db_path = db_path
    def write(self, signals):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                symbol TEXT,
                timestamp_IST TEXT,
                action TEXT,
                price REAL,
                status TEXT
            )
        ''')
        c.execute('DELETE FROM signals')  # Remove this line if you want to keep history
        for signal in signals:
            c.execute('''
                INSERT INTO signals (symbol, timestamp_IST, action, price, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (signal["symbol"], signal["timestamp_IST"], signal["action"], signal["price"], signal["status"]))
        conn.commit()
        conn.close()
