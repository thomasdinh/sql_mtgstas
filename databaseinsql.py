import mysql.connector
import array
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

def get_player_id(name):

    if name is None:
        return 0
    connection = None

    try:
        # Connect to the database
        connection = connect_to_database()
        cursor = connection.cursor()

        # Query to get the maximum entry count
        query = "SELECT * FROM player WHERE name = %s"
        cursor.execute(query, (name,))
        player_id_result = cursor.fetchone()
        player_id = player_id_result[0]
        #print(player_id)
        return player_id
    
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

def get_last_match_id():
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
        print(f'Last match_id: {pos_match_id}')
        return pos_match_id
    
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

def get_match_result(decklists,result):
    '''
    returns:
          - Deck_id of the winner
          - Deck_ids of losing decks in a array
    No draws build in yet
    '''
    winner = 1
    loser_decks = []
    
    if len(decklists) < 2:
        raise ValueError('Error: There are no decks provided! Or 2 decks are needed at least!')
    if len(result) != len(decklists):
        raise ValueError('Error: Matchresult is missing or results are missing!')
        
    
    arg_decklists_type = isinstance(decklists, list)
    arg_result_type = isinstance(result, list)

    if arg_decklists_type == False:
        raise ValueError('Error:  decklists is not a list!')
    if arg_result_type == False:
        raise ValueError('Error: result is not a list!')
    
    #print(f'{decklists[0]} type: {type(decklists[0])}')
    deck_ids = []
    if isinstance(decklists[0],str):
        deck_ids = get_all_player_ids(decklists)
        print(f'Decklist is in Strng: {deck_ids}')
    elif isinstance( decklists[0],int):
        deck_ids = decklists
        print(f'Decklist is in int: {deck_ids}')
    else:
        raise Error(f'Decklist element: {decklists[0]} is not in str or int, therefore cannot be evaluated!')
    
    #find winner and losers
    try:
        winner_index = result.index(1)
        #print(f"The index of {decklists[winner_index]} is {winner_index}.")
        winner = deck_ids[winner_index]
        loser_decks = deck_ids[:winner_index] + deck_ids[winner_index+1:]
        print(f'Winner: {winner} losers:{loser_decks}')
        return winner, loser_decks

    except ValueError:
        print(f"'No winner' is not in the list.")

def add_match_win(matchID, DeckID, OpponentDeckID, Result = None, Date = None):
    cur_date = get_current_date()
    cur_result = 1

    if Date != None:
        cur_date = Date
    
    if Result != None:
        cur_result = Result
    
    query = f"INSERT INTO deckwin (MatchID, DeckID, OpponentDeckID, Result, Date) VALUES (%s, %s, %s, %s, %s);"
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'Add to deckwin : {matchID}, {DeckID}')
        cursor.execute(query, (matchID, DeckID, OpponentDeckID, cur_result, cur_date ))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close() 
    
def del_match_win_entry(matchID):
    query = f"DELETE FROM deckwin WHERE MatchID = %s;"
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'DEL from deckwin : {matchID}')
        cursor.execute(query, (matchID,))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close()

def add_deck_lose(matchID, DeckID, OpponentDeckID, Result = None, Date = None):
    cur_date = get_current_date()
    cur_result = 1

    if Date != None:
        cur_date = Date
    
    if Result != None:
        cur_result = Result
    
    query = f"INSERT INTO decklose (MatchID, DeckID, OpponentDeckID, Result, Date) VALUES (%s, %s, %s, %s, %s);"
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'Add to decklose : {matchID}, {DeckID}')
        cursor.execute(query, (matchID, DeckID, OpponentDeckID, cur_result, cur_date ))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close()

def del_decklose_entry(matchID):
    query = f"DELETE FROM decklose WHERE MatchID = %s;"
    connection = None
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        print(f'DEL from decklose : matchid: {matchID}')
        cursor.execute(query, (matchID,))
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        if connection is not None:
            connection.rollback()
    finally:
        if connection is not None:
            connection.close()  

'''
"match_id","Decklist","match_result","date","group_id","comment"
1,"Otharri, Tymna, Urza","1, 0, 0","20.10.24",0,""
'''           
def eval_csv_line(decklist, match_result, match_id = None, date = None, group_id = None, comment = None):
    new_match_id = get_last_match_id() + 1
    new_date = get_current_date()
    new_group_id = 1
    new_comment = ""
    winner = 0
    losers = []
    
    if match_id != None:
        new_match_id = match_id
    
    if date != None:
        new_date = date

    if group_id != None:
        new_group_id = group_id

    if comment != None:
        new_comment= comment

    winner, losers = get_match_result(decklists= decklist, result= match_result)


def get_all_player_ids(playername_array):
    player_ids = []
    for player in playername_array:
        player_id = get_player_id(player)
        player_ids.append(player_id)
    print(player_ids)
    return player_ids

if __name__ == "__main__":
    connection = connect_to_database()
    del_decklose_entry(1)
    
     

