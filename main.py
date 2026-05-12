import os
import requests
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL")

# Database connection
conn = sqlite3.connect("sales_data.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_number TEXT,
    sale_date TEXT,
    transaction_time TEXT,
    sale_amount REAL,
    tax_amount REAL,
    discount_amount REAL,
    round_off REAL,
    net_sale REAL,
    payment_mode TEXT,
    order_type TEXT,
    transaction_status TEXT
)
""")

conn.commit()

# Retry mechanism
retries = 3

for attempt in range(retries):
    try:
        response = requests.get(API_URL)

        if response.status_code == 200:
            data = response.json()

            # Check API structure
            orders = data.get("data", [])

            for order in orders:

                receipt_number = order.get("receipt_number")
                sale_date = order.get("receipt_date", "")

                transaction_time = ""

                if sale_date:
                    try:
                        dt = datetime.strptime(
                            sale_date,
                            "%Y-%m-%d %H:%M:%S"
                        )
                        transaction_time = dt.strftime("%H:%M:%S")
                    except:
                        pass

                sale_amount = order.get("invoice_amount", 0)
                tax_amount = order.get("tax_amount", 0)
                discount_amount = order.get("discount_amount", 0)
                round_off = order.get("round_off", 0)
                net_sale = order.get("net_sale", 0)
                payment_mode = order.get("payment_mode", "")
                order_type = order.get("order_type", "")
                transaction_status = order.get("transaction_status", "")

                cursor.execute("""
                INSERT INTO sales_data (
                    receipt_number,
                    sale_date,
                    transaction_time,
                    sale_amount,
                    tax_amount,
                    discount_amount,
                    round_off,
                    net_sale,
                    payment_mode,
                    order_type,
                    transaction_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    receipt_number,
                    sale_date,
                    transaction_time,
                    sale_amount,
                    tax_amount,
                    discount_amount,
                    round_off,
                    net_sale,
                    payment_mode,
                    order_type,
                    transaction_status
                ))

            conn.commit()

            print("Data inserted successfully!")
            break

        else:
            print("API Error:", response.status_code)

    except Exception as e:
        print("Error:", e)

        if attempt < retries - 1:
            print("Retrying...")
            time.sleep(2)

conn.close()