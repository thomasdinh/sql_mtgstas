from databaseinsql import eval_csv_line
import pandas as pd

default_csv_file = 'test_data.csv'

def parse_match_result(result_str):
    # Remove square brackets if present
    result_str = result_str.strip('[]')
    # Split the string by commas and convert each element to an integer
    return [int(x.strip()) for x in result_str.split(',')]



def read_csv_mtgmatches(filename = None):
    if filename is None:
        filepath = default_csv_file
    else:
        filepath = filename
    data = pd.read_csv(filepath)
    
    for index, row in data.iterrows():
    # Convert the decklist and match_result strings to lists
        decklist_1 = [deck.strip() for deck in row['Decklist'].split(',')]
        stripped_results = parse_match_result(row['match_result'])


        eval_csv_line(
            decklist= decklist_1,
            match_result= stripped_results,
            date= row['date'],
            group_id= row['group_id']
        )
    
        
    print("CSV evaluation complete.")

if __name__ == "__main__":
    read_csv_mtgmatches()