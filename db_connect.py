import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connection successful!")
        conn.close()
    else:
        print("❌ Connection failed.")
