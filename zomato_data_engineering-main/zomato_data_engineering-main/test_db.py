import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password="ramesh@05\"",
        database='foods'
    )
    if connection.is_connected():
        print("✅ Connection successful!")
except Exception as e:
    print("❌ Connection failed:", e)
finally:
    if connection.is_connected():
        connection.close()
