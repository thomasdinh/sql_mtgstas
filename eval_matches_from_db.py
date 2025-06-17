import databaseinsql as dbsql
import pandas as pd
import mysql.connector

def get_wr_deck(id):
    connection = None
    try:
        # Connect to the database
        connection = dbsql.connect_to_database()
        cursor = connection.cursor()

        # SQL query to delete the entry with the maximum matchid
        query = ""

        # Execute the query
        cursor.execute(query)

        # Commit the changes to the database
        connection.commit()

    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()  # Rollback in case of error

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    pass
