import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        # Establish the database connection
        connection = mysql.connector.connect(
            host='localhost',
            database='mtgmatches2', 
            user='root', 
            password='101010',
            auth_plugin='mysql_native_password' 
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

def get_deck_id(deckname, database_connection=None):
    connection = connect_to_database()
    data = []
    if database_connection is not None:
        connection = database_connection

    cursor = None
    try:
        if connection is None:
            print("Failed to establish a database connection.")
            return

        cursor = connection.cursor()
        query = "SELECT DeckID FROM deck WHERE Deckname = %s"
        cursor.execute(query, (deckname,))

        # Fetch all rows from the executed query
        rows = cursor.fetchall()
        for row in rows:
            print(f'this is row: {row}')
            data.append(row[0])
            
        if data == []:
            print(f'Deck {deckname} is not in database')
            return None
        else:
            print(data[0])
            return(data[0])

    except Error as e:
        print(f"Error: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL connection is closed")

def add_mtgmatch(decklist, winnerID, matchID = None, date = None, database_connection=None ):
    connection = connect_to_database()
    
    if database_connection is not None:
        connection = database_connection

    cursor = None
    try:
        if connection is None:
            print("Failed to establish a database connection.")
            return

        cursor = connection.cursor()
        id_qeuery = "SELECT COUNT(MatchID) FROM mtgmatches;"
        id = matchID
        if id == None:
            id = query_requests(query= id_qeuery,connection=connection)
            print(id[0])
        #query = "INSERT Into MTGMatches (matchid, decklists,data,winnerid) \n" \
        #"VALUES (%s, %s, %s, %s)"
        #cursor.execute(query, (decklist,))

        

    except Error as e:
        print(f"Error: {e}")

def convert_decklist_to_array(decklist):
    array = decklist.split(",")
    array = [element.strip() for element in array]
    print(array)
    return array

def deckarray_to_deck_id_array(decklist_array):
    deck_ids = []
    for deck in decklist_array:
        deck_id = get_deck_id(deck)
        if deck_id == None:
            print("Please add the missing deck to the table. Metrics will fail otherwise")
        deck_ids.append(deck_id)
    print(deck_ids)
    return deck_ids

def delete_max_matchid_entry(table_name):
    connection = None
    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # SQL query to delete the entry with the maximum matchid
        query = f"""
            DELETE FROM {table_name}
            WHERE matchid = (
                SELECT max_matchid FROM (
                    SELECT MAX(matchid) AS max_matchid FROM {table_name}
                ) AS temp
            );
        """

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




def add_mtgmatches_entry(decklists, winnerID, date=None, matchID=None):
    connection = None
    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Query to get the maximum entry count
        max_entry_count_query = "SELECT COUNT(*) FROM mtgmatches"
        cursor.execute(max_entry_count_query)
        max_entry_result = cursor.fetchone()
        pos_match_id = max_entry_result[0]

        # Prepare data for insertion
        data = []
        if matchID is not None:
            data.append(matchID)
        else:
            data.append(pos_match_id + 1)  # Increment to get the next ID
        data.append(decklists)
        if date is None:
            current_date = "25-05-2025"  # Use the correct date format for your database
        else:
            current_date = date
        data.append(current_date)
        data.append(winnerID)
        print(data)

        # SQL query to insert data
        query = "INSERT INTO mtgmatches (matchid, decklists, date, winnerID) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, tuple(data))

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

def add_deck_win_entry(matchID, deckID, deckopponentID, result, date = None, ):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        query = "INSERT Into deckwin (matchid, deckid, opponentDeckID,result, date) \n" \
            "VALUES (%s, %s, %s, %s, %s);"
    
        if date == None:
            current_date = "25-05-2025"
        else:
            current_date = date
        data = []
        data.append(matchID)
        data.append(deckID)
        data.append(deckopponentID)
        data.append(result)
        data.append(current_date)
        print(data)
        cursor.execute(query, tuple(data))
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
    connection = connect_to_database()
    test_array = convert_decklist_to_array('Ghired, Obeka 2, Obeka, Bethor')
    #add_deck_win_entry(matchID = 1, deckID = 1, deckopponentID =2, result= 1, date = None)
    delete_max_matchid_entry('deckwin')

