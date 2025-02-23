import sqlite3

# Connect to the SQLite database
DATABASE = 'data.db'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Query all rows from the csv_data table
cursor.execute("SELECT * FROM csv_data")
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the connection
conn.close()