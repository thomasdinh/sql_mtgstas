import databaseinsql as dbsql
import pandas as pd
import mysql.connector
import logging


def flatten_single_tuple_list(tuple_list):
    return [item[0] for item in tuple_list]

def matches_won_by_deck(id, connection = None):
    current_connection = dbsql.connect_to_database()
    if connection != None:
        current_connection = connection
    try:
        with current_connection.cursor() as cursor:
            win_query = "SELECT matchid FROM mtgmatches WHERE winnerID = %s"
            cursor.execute(win_query, (id,))
            win_results = flatten_single_tuple_list(cursor.fetchall())
            return(win_results)

    except Exception as e:
        print("An unexpected error occurred: %s", e)

def matches_lost_by_deck(id, connection = None):
    current_connection = dbsql.connect_to_database()
    if connection != None:
        current_connection = connection
    try:
        with current_connection.cursor() as cursor:
            lose_query = "SELECT matchid FROM decklose WHERE deckid = %s"
            cursor.execute(lose_query, (id,))
            lose_results = flatten_single_tuple_list(cursor.fetchall())
            return(lose_results)

    except Exception as e:
        print("An unexpected error occurred: %s", e)

def matches_played(id, connection = None):
    current_connection = dbsql.connect_to_database()
    if connection != None:
        current_connection = connection
    
    loses =matches_lost_by_deck(id, current_connection)
    wins = matches_won_by_deck(id, current_connection)
    return loses + wins


def get_wr_deck(deck_id, connection = None):
    try:
        current_connection = dbsql.connect_to_database()
        if connection != None:
            current_connection = connection
        loses = len(matches_lost_by_deck(id=deck_id, connection= current_connection))
        wins = len(matches_won_by_deck(id=deck_id, connection= current_connection))
        winrate = (wins*100)/(wins +loses)
        return winrate


    except Exception as e:
        print("An unexpected error occurred: %s", e)

if __name__ == "__main__":
    print(matches_played(11))
    
