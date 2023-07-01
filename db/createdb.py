import MySQLdb as mysql

# Connect to the MySQL server
cnx = mysql.connect(
    host='localhost',
    user='root',
    password='',
    database='test'
)

# Create a cursor object
cursor = cnx.cursor()

# Read the SQL dump file
with open('flask.sql', 'r') as file:
    sql_dump = file.read()

# Split the SQL dump into separate statements
statements = sql_dump.split(';')

# Execute each statement
for statement in statements:
    if statement.strip():  # Skip empty statements
        cursor.execute(statement)

# Commit the changes
cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()
