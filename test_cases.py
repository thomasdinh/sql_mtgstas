import databaseinsql

if __name__ == "__main__":
    connection = databaseinsql.connect_to_database()
    test_array = databaseinsql.convert_decklist_to_array('Ghired, Obeka 2, Obeka, Bethor')
    databaseinsql.add_mtgmatches_entry(winnerID=1, decklists='1,2,3,4')