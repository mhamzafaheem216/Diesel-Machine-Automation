import mysql.connector
from config import DB_CONFIG

class DatabaseError(Exception):
    pass

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

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
        cursor.execute(
            """
            INSERT INTO card_balances (card_number, fuel_balance, card_type, last_updated)
            VALUES (%s, %s, %s, NOW())
            """,
            (card_number, fuel_balance, card_type)
        )
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
        raise DatabaseError(f"DB Error in insert_card_balance: {e}")

def update_card_balance(card_number, fuel_balance):
    """
    Update fuel_balance and last_updated for an existing card by card_number.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE card_balances
            SET fuel_balance = %s, last_updated = NOW()
            WHERE card_number = %s
            """,
            (fuel_balance, card_number)
        )
        conn.commit()
        conn.close()
    except mysql.connector.Error as e:
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
