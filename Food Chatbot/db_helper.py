import mysql.connector
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize global cnx as None
global cnx
cnx = None

def reconnect():
    global cnx
    try:
        # Only check is_connected if cnx is not None
        if cnx is not None and cnx.is_connected():
            logging.info("Database connection already active")
            return
        # Establish new connection
        cnx = mysql.connector.connect(
            host="localhost",
            port=3305,
            user="root",
            password="1234",
            database="pandeyji_eatery"
        )
        logging.info("Database connection established")
    except mysql.connector.Error as err:
        logging.error(f"Failed to connect to database: {err}")
        cnx = None

# Initial connection attempt
reconnect()

def insert_order_item(food_item, quantity, order_id):
    if not cnx or not cnx.is_connected():
        reconnect()
    if not cnx:
        logging.error("No database connection available")
        return -1
    try:
        cursor = cnx.cursor()
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        logging.info(f"Inserted order item: {food_item}, quantity: {quantity}, order_id: {order_id}")
        return 1
    except mysql.connector.Error as err:
        logging.error(f"Error inserting order item: {err}")
        cnx.rollback()
        return -1
    finally:
        if 'cursor' in locals():
            cursor.close()

def insert_order_tracking(order_id, status):
    if not cnx or not cnx.is_connected():
        reconnect()
    if not cnx:
        logging.error("No database connection available")
        return
    try:
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)", (order_id, status))
        cnx.commit()
        logging.info(f"Inserted order tracking: order_id={order_id}, status={status}")
    except mysql.connector.Error as err:
        logging.error(f"Database error in insert_order_tracking: {err}")
        cnx.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()

def get_total_order_price(order_id):
    if not cnx or not cnx.is_connected():
        reconnect()
    if not cnx:
        logging.error("No database connection available")
        return 0.0
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT get_total_order_price(%s)", (order_id,))
        result = cursor.fetchone()[0]
        total = float(result) if result is not None else 0.0
        logging.info(f"Total order price for order_id {order_id}: {total}")
        return total
    except mysql.connector.Error as err:
        logging.error(f"Database error in get_total_order_price: {err}")
        return 0.0
    finally:
        if 'cursor' in locals():
            cursor.close()

def get_next_order_id():
    if not cnx or not cnx.is_connected():
        reconnect()
    if not cnx:
        logging.error("No database connection available")
        return -1
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT MAX(order_id) FROM orders")
        result = cursor.fetchone()[0]
        next_id = 1 if result is None else result + 1
        logging.info(f"Next order_id: {next_id}")
        return next_id
    except mysql.connector.Error as err:
        logging.error(f"Database error in get_next_order_id: {err}")
        return -1
    finally:
        if 'cursor' in locals():
            cursor.close()

def get_order_status(order_id):
    if not cnx or not cnx.is_connected():
        reconnect()
    if not cnx:
        logging.error("No database connection available")
        return None
    try:
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        status = result[0] if result else None
        logging.info(f"Order status for order_id {order_id}: {status}")
        return status
    except mysql.connector.Error as err:
        logging.error(f"Database error in get_order_status: {err}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in get_order_status: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()