import databaseinsql as dbsql

if __name__ == "__main__":
    connection = dbsql.connect_to_database()
    test_array = dbsql.convert_decklist_to_array('Ghired, Obeka 2, Obeka, Bethor')
    dbsql.add_mtgmatches_entry(winnerID=1, decklists='1,2,3,4')
    dbsql.delete_all_entries('decklose')
    dbsql.delete_all_entries('deckwin')
    dbsql.delete_all_entries('mtgmatches')