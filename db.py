import mysql.connector
from config import DB_CONFIG

class DatabaseError(Exception):
    pass

def get_db_connection():
    try:
        print(f"[DB DEBUG] Connecting to database at {DB_CONFIG['host']} as {DB_CONFIG['user']}")
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print(f"[DB DEBUG] Connected successfully to {DB_CONFIG['database']} database")
            return conn
        else:
            print(f"[DB ERROR] Failed to connect but no exception raised")
            raise DatabaseError("Failed to connect to database")
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Connection failed: {e}")
        raise DatabaseError(f"Connection failed: {e}")

# ======================
# AUDIT LOG
# ======================
def insert_audit_log(raw_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_log (raw_data) VALUES (%s)",
            (raw_data,)
        )
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        raise DatabaseError(f"DB Error in insert_audit_log: {e}")

# ======================
# TRANSACTION LOG
# ======================
def insert_transaction(card_number, fuel_used):
    """
    Insert a new transaction record.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transaction_log (card_number, fuel_info) VALUES (%s, %s)",
            (card_number, fuel_used)
        )
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        raise DatabaseError(f"DB Error in insert_transaction: {e}")

# ======================
# CARD BALANCES
# ======================
def insert_card_balance(card_number, fuel_balance, card_type=None):
    """
    Insert a new card balance row.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Debug info before executing
        print(f"[DB DEBUG] Creating new card #{card_number} with balance {fuel_balance}L, type: {card_type}")
        
        cursor.execute(
            """
            INSERT INTO card_balances (card_number, fuel_balance, card_type, last_updated)
            VALUES (%s, %s, %s, NOW())
            """,
            (card_number, fuel_balance, card_type)
        )
        
        # Check the new row ID
        last_id = cursor.lastrowid
        print(f"[DB DEBUG] Created card #{card_number} with ID {last_id}")
        
        conn.commit()
        conn.close()
        print(f"[DB DEBUG] Successfully committed new card #{card_number}")
        
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Failed to create card #{card_number}: {e}")
        raise DatabaseError(f"DB Error in insert_card_balance: {e}")

def update_card_balance(card_number, fuel_balance):
    """
    Update fuel_balance and last_updated for an existing card by card_number.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Debug info before executing
        print(f"[DB DEBUG] Updating card #{card_number} to balance {fuel_balance}L")
        
        # Execute the update
        cursor.execute(
            """
            UPDATE card_balances
            SET fuel_balance = %s, last_updated = NOW()
            WHERE card_number = %s
            """,
            (fuel_balance, card_number)
        )
        
        # Check rows affected
        rows_affected = cursor.rowcount
        print(f"[DB DEBUG] Rows affected by update: {rows_affected}")
        
        # If no rows affected, card doesn't exist yet
        if rows_affected == 0:
            print(f"[DB DEBUG] Card #{card_number} doesn't exist - will need to create it")
            # We'll let the calling code handle this by raising an error
            conn.commit()
            conn.close()
            raise DatabaseError(f"Card {card_number} not found")
        
        # Commit and close
        conn.commit()
        conn.close()
        print(f"[DB DEBUG] Successfully updated card #{card_number}")
        
    except mysql.connector.Error as e:
        print(f"[DB ERROR] Failed to update card #{card_number}: {e}")
        raise DatabaseError(f"DB Error in update_card_balance: {e}")

def get_card_balance(card_number):
    """
    Retrieve card balance by card_number.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM card_balances WHERE card_number = %s",
            (card_number,)
        )
        row = cursor.fetchone()
        conn.close()
        return row
    except mysql.connector.Error as e:
        raise DatabaseError(f"DB Error in get_card_balance: {e}")
