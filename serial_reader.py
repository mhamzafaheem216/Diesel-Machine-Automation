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
    # Skip empty data
    if not raw_data or not raw_data.strip():
        return False
        
    try:
        # Insert raw data into audit log for reference
        db.insert_audit_log(raw_data)
        
        # CARD BALANCE FORMAT
        balance_match = re.search(r'C#(\d+)-([\d\.]+)L', raw_data)
        if balance_match:
            card_id, liters_left = balance_match.groups()
            print(f"→ Card balance match: Card #{card_id} with {liters_left}L")
            
            try:
                # Try to update existing card
                print(f"→ Attempting to update card #{card_id} in database...")
                db.update_card_balance(card_id, float(liters_left))
                print(f"→ Database update successful for card #{card_id}")
                return True
            except DatabaseError as db_err:
                # Card doesn't exist yet, create it
                print(f"→ Update failed: {db_err}")
                try:
                    print(f"→ Attempting to create new card #{card_id}...")
                    db.insert_card_balance(card_id, float(liters_left), "Standard")
                    print(f"→ Successfully created card #{card_id} in database")
                    return True
                except DatabaseError as db_err:
                    print(f"[DB ERROR] Card creation failed: {db_err}")
                    return False
        
        # TRANSACTION FORMAT
        # Debug output to find hidden characters
        if "Card:" in raw_data and "Sale:" in raw_data and "Bal:" in raw_data:
            print(f"→ TRANSACTION DEBUG: Found transaction keywords")
            print(f"→ TRANSACTION DEBUG: Raw data length: {len(raw_data)}")
            print(f"→ TRANSACTION DEBUG: ASCII codes: {[ord(c) for c in raw_data[:20]]}")

        # More flexible transaction pattern (allows for various whitespace)
        transaction_match = re.search(r'Card:(\d+)\s+Sale:([\d\.]+)L\s+Bal:([\d\.]+)L', raw_data)
        if transaction_match:
            card_id, liters_used, liters_left = transaction_match.groups()
            print(f"→ Transaction match: Card #{card_id} used {liters_used}L, has {liters_left}L left")
            
            try:
                # Check if card exists
                card = db.get_card_balance(card_id)
                if not card:
                    # Card doesn't exist yet, create it first
                    print(f"→ Card #{card_id} doesn't exist, creating it")
                    db.insert_card_balance(card_id, float(liters_left), "Standard")
                    print(f"→ Created new card #{card_id}")
                
                # Now add the transaction and update balance
                db.insert_transaction(card_id, float(liters_used))
                db.update_card_balance(card_id, float(liters_left))
                print(f"→ Transaction recorded: Card #{card_id} used {liters_used}L")
                return True
            except DatabaseError as db_err:
                print(f"[DB ERROR] Transaction failed for card {card_id}: {db_err}")
                return False
        
        # NO MATCH - Try one more fallback pattern for transactions
        transaction_fallback = re.search(r'Card[:\s]*(\d+)[^\d]+([\d\.]+)L[^\d]+Bal[:\s]*([\d\.]+)L', raw_data)
        if transaction_fallback:
            card_id, liters_used, liters_left = transaction_fallback.groups()
            print(f"→ Transaction fallback match: Card #{card_id} used {liters_used}L, has {liters_left}L left")
            
            try:
                # Check if card exists
                card = db.get_card_balance(card_id)
                if not card:
                    # Card doesn't exist yet, create it first
                    print(f"→ Card #{card_id} doesn't exist, creating it")
                    db.insert_card_balance(card_id, float(liters_left), "Standard")
                    print(f"→ Created new card #{card_id}")
                
                # Now add the transaction and update balance
                db.insert_transaction(card_id, float(liters_used))
                db.update_card_balance(card_id, float(liters_left))
                print(f"→ Transaction recorded: Card #{card_id} used {liters_used}L")
                return True
            except DatabaseError as db_err:
                print(f"[DB ERROR] Transaction failed for card {card_id}: {db_err}")
                return False
        
        # TRULY NO MATCH
        print(f"[WARNING] Unrecognized format: {raw_data}")
        print(f"[DEBUG] Raw data bytes: {raw_data.encode()}")
        return False
            
    except DatabaseError as db_err:
        print(f"[DB ERROR] Database operation failed: {db_err}")
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to process data: {e}")
        return False

def start_serial_reading(debug=True):
    try:
        ser = serial.serial_for_url(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")

        # Simulated test data (for debugging only)
        # test_data = [
        #     "C#12345-100.00L\n",
        #     "Card:12345 Sale:5.00L Bal:95.00L\n",
        #     "Card:67890 Sale:10.00L Bal:90.00L\n"
        # ]
        #
        # # Send test data into the loop
        # for line in test_data:
        #     ser.write(line.encode())
        #     time.sleep(0.5)

        while True:
            line = ser.readline().decode("utf-8").strip()
            if not line:  # Skip empty lines
                continue
                
            print(f"Received: {line}")
            
            # TRANSACTION FORMAT
            # Check if it's a transaction record (Card:XX Sale:XX.XXL Bal:XX.XXL)
            if "Card:" in line and "Sale:" in line and "Bal:" in line:
                print("*** PROCESSING TRANSACTION RECORD ***")
                print(f"Debug - Raw bytes: {line.encode()}")
                print(f"Debug - Hex: {' '.join([hex(ord(c)) for c in line])}")
                result = parse_serial_data(line)
                if result:
                    print("✓ Transaction processed successfully")
                else:
                    print("✗ Failed to process transaction")
            
            # MULTIPLE CARD RECORDS FORMAT
            # Check if we received multiple card records in one line (contains multiple C#XX-XXX.XXL)
            elif "C#" in line and " C#" in line:  # Multiple card balance records
                print("*** PROCESSING MULTIPLE CARD RECORDS ***")
                
                # Extract all card balance records using regex
                records = re.findall(r'C#\d+-\d+\.\d+L', line)
                
                # If no matches, try simpler patterns
                if not records:
                    potential_records = []
                    for part in line.split():
                        if part.startswith("C#") and part.endswith("L"):
                            potential_records.append(part)
                    records = potential_records
                
                print(f"Found {len(records)} card records")
                if len(records) > 0:
                    print(f"Example records: {records[:3]}")
                
                # Process each record individually
                success_count = 0
                for record in records:
                    print(f"Processing record: {record}")
                    if parse_serial_data(record):
                        success_count += 1
                
                print(f"✓ Successfully processed {success_count} out of {len(records)} card records")
            
            # SINGLE CARD RECORD FORMAT
            # Process as a single card balance record (C#XX-XXX.XXL)
            elif "C#" in line:
                print("*** PROCESSING SINGLE CARD RECORD ***")
                if parse_serial_data(line):
                    print("✓ Card record processed successfully")
                else:
                    print("✗ Failed to process card record") 
            
            # UNKNOWN FORMAT
            else:
                print(f"⚠ Unknown data format: {line}")
                parse_serial_data(line)

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    start_serial_reading()
