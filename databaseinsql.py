import mysql.connector
from datetime import datetime
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

def get_current_date():
    return datetime.today().strftime('%d.%m.%y')

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

def delete_max_matchid_entry_deckwin():
    connection = None
    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # SQL query to delete the entry with the maximum matchid
        query = f"""
            DELETE FROM deckwin
            WHERE matchid = (
                SELECT max_matchid FROM (
                    SELECT MAX(matchid) AS max_matchid FROM deckwin
                ) AS temp
            );
        """

        """ Error: 1093 (HY000): You can't specify target table 'deckwin' for update in FROM clause
        occurs because MySQL does not allow you to update or delete rows from a table and select from the same table in a subquery within the same SQL statement.
        Solutions to the Problem

        There are a few ways to work around this limitation:

        Use a Temporary Table:
            Store the result of the subquery in a temporary table and then use this temporary table in your main query.

        Use a Derived Table:
            Use a derived table (a subquery in the FROM clause) to achieve the same result. """

        

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


def add_mtgmatches_entry(decklists, winnerID, date=None, matchID=None, groupID = None):
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
            current_date = get_current_date()  # Use the correct date format for your database
        else:
            current_date = date
        data.append(current_date)
        data.append(winnerID)
        if groupID == None:
            data.append(1)
        else:
            data.append(groupID)
        print(data)

        # SQL query to insert data
        query = "INSERT INTO mtgmatches (matchid, decklists, date, winnerID, groupID) VALUES (%s, %s, %s, %s, %s);"
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

def del_mtgmatches_entry(matchID= None):
    to_del_entry = matchID
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
        if to_del_entry == None:
            to_del_entry = pos_match_id
        
        del_mtg_match_query = "DELETE FROM mtgmatches WHERE matchID = %s"
        cursor.execute(del_mtg_match_query, (to_del_entry,))
        connection.commit()

    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()  # Rollback in case of error

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

def delete_deck_win(matchID=None):
    connection = None
    cursor = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        if matchID is not None:
            query = "DELETE FROM deckwin WHERE matchid = %s;"
            cursor.execute(query, (matchID,))
        else:
            # Find the maximum matchID
            query_max_id = "SELECT MAX(matchid) FROM deckwin;"
            cursor.execute(query_max_id)
            max_id = cursor.fetchone()[0]

            if max_id is not None:
                query = "DELETE FROM deckwin WHERE matchid = %s;"
                cursor.execute(query, (max_id,))
                print(f"Deleted entry with max matchID: {max_id}")
            else:
                print("No entries found in the table.")

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

# Result 0 - Lose, 1 - Draw
def add_deck_lose(matchID, deckID, OpponenDeckID, Result, date = None):
    current_date = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        query = "INSERT Into decklose (matchid, deckid, opponentDeckID,result, date) \n" \
            "VALUES (%s, %s, %s, %s, %s);"
    
        if date == None:
            current_date = get_current_date()
        else:
            current_date = date
        data = []
        data.append(matchID)
        data.append(deckID)
        data.append(OpponenDeckID)
        data.append(Result)
        data.append(current_date)
        print(f'Add to decklose : {data}')
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

def delete_deck_lose(matchID=None):
    connection = None
    cursor = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()

        if matchID is not None:
            query = "DELETE FROM decklose WHERE matchid = %s;"
            cursor.execute(query, (matchID,))
        else:
            # Find the maximum matchID
            query_max_id = "SELECT MAX(matchid) FROM decklose;"
            cursor.execute(query_max_id)
            max_id = cursor.fetchone()[0]

            if max_id is not None:
                query = "DELETE FROM decklose WHERE matchid = %s;"
                cursor.execute(query, (max_id,))
                print(f"Deleted entry with max matchID: {max_id}")
            else:
                print("No entries found in the table.")

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

def add_player_to_playgroup(playerID, groupID):
    query = f"INSERT INTO playgroupplayer (GroupID, playerID) VALUES (%s, %s);"
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'Add to playgroupplayer : {groupID}, {playerID}')
        cursor.execute(query, (groupID,playerID))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close() 
  
def del_player_from_playgroup(groupID,playerID):
    query = f'DELETE FROM playgroupplayer WHERE groupid = %s AND playerid =%s;'
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'DEL player {playerID} from playgroup : {groupID}')
        cursor.execute(query, (groupID,playerID))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close() 

if __name__ == "__main__":
    connection = connect_to_database()
    add_mtgmatches_entry(decklists= '2,5,7,10', winnerID= 5, date=None, matchID=None, groupID = None)

    
     

