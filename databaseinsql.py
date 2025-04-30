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

def track_losses_against_decks(deckname):
    data = all_info_matches_of_deck(deckname=deckname)
    losses = {}

    deckname = deckname.strip()  # Strip whitespace from the deckname

    for match in data:
        decklist = [name.strip() for name in match[1].split(',')]  # Strip whitespace from each name in the decklist
        result = list(map(int, match[2].strip('[]').split(',')))

        if deckname in decklist:
            player_index = decklist.index(deckname)
            if result[player_index] == 0:  # Ghired lost the match
                for opponent in decklist:
                    if opponent != deckname:
                        if opponent not in losses:
                            losses[opponent] = 0
                        losses[opponent] += 1

    return losses

def calculate_win_rate_against_decks(deckname):
    data = all_info_matches_of_deck(deckname=deckname)
    win_loss_record = {}

    deckname = deckname.strip()  # Strip whitespace from the deckname

    for match in data:
        decklist = [name.strip() for name in match[1].split(',')]  # Strip whitespace from each name in the decklist
        result = list(map(int, match[2].strip('[]').split(',')))

        if deckname in decklist:
            player_index = decklist.index(deckname)
            for opponent in decklist:
                if opponent != deckname:
                    if opponent not in win_loss_record:
                        win_loss_record[opponent] = {'wins': 0, 'losses': 0}
                    if result[player_index] == 1:  # Ghired won the match
                        win_loss_record[opponent]['wins'] += 1
                    else:  # Ghired lost the match
                        win_loss_record[opponent]['losses'] += 1

    win_rate_record = {}
    for opponent, record in win_loss_record.items():
        total_matches = record['wins'] + record['losses']
        if total_matches > 0:
            win_rate = (record['wins'] / total_matches) * 100
        else:
            win_rate = 0
        win_rate_record[opponent] = win_rate

    return win_rate_record

def use_cases_examples():
    win_rate_record = calculate_win_rate_against_decks('Ghired')
    print("Win rate for 'Ghired' against decks:")
    for opponent, win_rate in win_rate_record.items():
        print(f"{opponent}: {win_rate:.2f}%")

    print("Losses for 'Ghired' against decks:")
    losses = track_losses_against_decks('Ghired')
    for opponent, count in losses.items():
        print(f"{opponent}: {count} losses")

if __name__ == "__main__":
    use_cases_examples()    