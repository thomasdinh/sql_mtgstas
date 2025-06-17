import mysql.connector
from datetime import datetime
from mysql.connector import Error

def connect_to_database():
    """Establish and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='mtgmatches2',
            user='root',
            password='101010',
            auth_plugin='mysql_native_password'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_current_date():
    """Return the current date in a specific format."""
    return datetime.today().strftime('%d.%m.%y')

def execute_query(connection, query, params=None):
    """Execute a given SQL query with optional parameters and return the results."""
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()

def get_deck_id(deckname, connection):
    """Retrieve the deck ID for a given deck name."""
    query = "SELECT DeckID FROM deck WHERE Deckname = %s"
    result = execute_query(connection, query, (deckname,))
    return result[0][0] if result else None

def get_all_deck_ids(decknamelist, connection):
    """Retrieve deck IDs for a list of deck names."""
    return [get_deck_id(deck, connection) for deck in decknamelist]

def add_mtgmatches_entry(decklists, winnerID, connection, date=None, matchID=None, groupID=None):
    """Add an entry to the mtgmatches table."""
    decklists_str = ', '.join(decklists)
    current_date = date or get_current_date()
    pos_match_id = matchID or get_max_id(connection, "mtgmatches") + 1
    groupID = groupID or 1

    query = "INSERT INTO mtgmatches (matchid, decklists, date, winnerID, groupID) VALUES (%s, %s, %s, %s, %s)"
    execute_query(connection, query, (pos_match_id, decklists_str, current_date, winnerID, groupID))

def get_max_id(connection, table_name):
    """Get the maximum ID from a specified table."""
    query = f"SELECT COUNT(*) FROM {table_name}"
    result = execute_query(connection, query)
    return result[0][0] if result else 0

def get_match_result(decklists, result):
    """Determine the winner and losers from a match result."""
    if len(decklists) < 2 or len(result) != len(decklists):
        raise ValueError("Invalid decklists or result length.")

    deck_ids = [get_deck_id(deck) for deck in decklists] if isinstance(decklists[0], str) else decklists
    winner_index = result.index(1)
    return deck_ids[winner_index], deck_ids[:winner_index] + deck_ids[winner_index+1:]

def add_match_win(matchID, deckID, opponentDeckID, connection, result=None, date=None):
    """Add a win entry to the deckwin table."""
    current_date = date or get_current_date()
    result = result or 1
    query = "INSERT INTO deckwin (MatchID, DeckID, OpponentDeckID, Result, Date) VALUES (%s, %s, %s, %s, %s)"
    execute_query(connection, query, (matchID, deckID, opponentDeckID, result, current_date))

def add_deck_lose(matchID, deckID, opponentDeckID, connection, result=None, date=None):
    """Add a loss entry to the decklose table."""
    current_date = date or get_current_date()
    result = result or 0
    query = "INSERT INTO decklose (MatchID, DeckID, OpponentDeckID, Result, Date) VALUES (%s, %s, %s, %s, %s)"
    execute_query(connection, query, (matchID, deckID, opponentDeckID, result, current_date))

def eval_csv_line(decklist, match_result, connection, match_id=None, date=None, group_id=None):
    """Evaluate a CSV line and update the database accordingly."""
    new_match_id = match_id or get_max_id(connection, "mtgmatches") + 1
    new_date = date or get_current_date()
    new_group_id = group_id or 1

    winner, losers = get_match_result(decklist, match_result)
    add_mtgmatches_entry(decklist, winner, connection, new_date, new_match_id, new_group_id)

    for loser in losers:
        add_match_win(new_match_id, winner, loser, connection, date=new_date)
        add_deck_lose(new_match_id, loser, winner, connection, date=new_date)

def main():
    connection = connect_to_database()
    if connection:
        try:
            # Example usage
            result = get_max_id(connection, 'decklose')
            print(result)
        finally:
            connection.close()

if __name__ == "__main__":
    main()
