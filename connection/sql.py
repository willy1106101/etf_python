import mysql.connector

# == Connection to MySQL Database default setting ===
host = 'localhost'
user = 'root'
password = '0110936'
database = 'etf'


# == Function to create a connection to the MySQL database ===

def create_connection(host, user, password, database):
    """Create a database connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# Create a connection to the database
def main():
    conn = create_connection(host, user, password, database)
    return conn 