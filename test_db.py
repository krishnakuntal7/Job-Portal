import mysql.connector
import os
from dotenv import load_dotenv

print("Starting test...")

load_dotenv()

print("Connecting to MySQL...")

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=5,
        use_pure=True
    )

    print("Database connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")

    result = cursor.fetchone()

    print("Number of jobs:", result[0])

    cursor.close()
    connection.close()

    print("Test completed successfully!")

except Exception as e:
    print("DATABASE ERROR:")
    print(type(e).__name__)
    print(str(e))