import re
import serial
import time
from config import SERIAL_PORT, BAUD_RATE
from db import DatabaseError
import db

def parse_serial_data(raw_data):
    """
    Expected formats:
    - C#12345-100.00L   (card balance info)
    - Card:12345 Sale:5.00L Bal:95.00L  (transaction info)
    """
    try:
    
        db.insert_audit_log(raw_data)  # Save raw data to audit log

        balance_pattern = r"C#(\d+)-([\d\.]+)L"
        transaction_pattern = r"Card:(\d+) Sale:([\d\.]+)L Bal:([\d\.]+)L"

        if match := re.match(balance_pattern, raw_data):
            card_id, liters_left = match.groups()
            db.update_card_balance(card_id, float(liters_left))

        elif match := re.match(transaction_pattern, raw_data):
            card_id, liters_used, liters_left = match.groups()
            db.insert_transaction(card_id, float(liters_used))
            db.update_card_balance(card_id, float(liters_left))
            
    except DatabaseError as db_err:
        print(f"[DB ERROR] Error In Database Operations : {db_err}")
        
    except Exception as e:
        print(f"[ERROR] Failed To Process Data : {e}")

def start_serial_reading():
    # Use serial_for_url so loop:// works
    try:
        ser = serial.serial_for_url(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT}...")

        # Simulated test data
        test_data = [
            "C#12l345-100.00L\n",
            "Card:12345 Sale:5.00L Bal:95.00L\n",
            "Card:67890 Sale:10.00L Bal:90.00L\n"
        ]

        # Send test data into the loop
        for line in test_data:
            ser.write(line.encode())
            time.sleep(0.5)

        # Read from the same port
        while True:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    print(f"Received: {line}")
                    parse_serial_data(line)
            except Exception as e:
                print(f"[ERROR] Serial read/process failed: {e}")
                time.sleep(1)
                
    except serial.SerialException as e:
        print(f"[ERROR] Could not start serial reading at Port  {SERIAL_PORT}: {e}")

if __name__ == "__main__":
    start_serial_reading()
