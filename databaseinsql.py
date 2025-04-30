import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host='localhost',
            database='mtgmatches', 
            user='root', 
            password='101010' 
        )

        if connection.is_connected():
            print("Connected to MySQL database")
            return connection

    except Error as e:
        print(f"Error: {e}")
        return None

def execute_query(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM mtgmatches"
        cursor.execute(query)

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Print the fetched rows
        for row in rows:
            print(row)

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def query_requests(connection, query):
    data = []
    try:
        cursor = connection.cursor()
       
        cursor.execute(query)

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Print the fetched rows
        for row in rows:
            #print(row)
            data.append(row)

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
            return data

def all_info_matches_of_deck(deckname):
    connection = connect_to_database()
    try:
        data = []
        cursor = connection.cursor()
        query = f"SELECT * FROM mtgmatches WHERE Decklist LIKE '%{deckname}%' ORDER BY date ASC;"
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except Error as e:
        print(f"Error: {e}")


def calculate_win_rate_deck(deckname):
    data = all_info_matches_of_deck(deckname=deckname)
    total_matches = 0
    matches_won = 0

    deckname = deckname.strip()  # Strip whitespace from the deckname

    for match in data:
        decklist = [name.strip() for name in match[1].split(',')]  # Strip whitespace from each name in the decklist
        result = list(map(int, match[2].strip('[]').split(',')))

        if deckname in decklist:
            total_matches += 1
            player_index = decklist.index(deckname)
            if result[player_index] == 1:
                matches_won += 1

    if total_matches == 0:
        return 0

    win_rate = (matches_won / total_matches) * 100
    return win_rate

if __name__ == "__main__":
    print(calculate_win_rate_deck('Eluge'))