from databaseinsql import eval_csv_line
import pandas as pd

default_csv_file = 'test_data.csv'

def strip_brackets(result: str) -> str:
    """Strip brackets from the match result string."""
    return result.strip('[]')



def read_csv_mtgmatches(filename = None):
    if filename is None:
        filepath = default_csv_file
    else:
        filepath = filename
    data = pd.read_csv(filepath)
        # Iterate over the DataFrame and apply the eval_csv_line function
    for index, row in data.iterrows():
    # Convert the decklist and match_result strings to lists
        decklist_1 = row['Decklist'].split(', ')
        stripped_results = strip_brackets(row['match_result'])
        match_result_1 = list(map(int, stripped_results.split(",")))
        print(decklist_1)
        print(match_result_1)

        eval_csv_line(
            decklist= decklist_1,
            match_result= match_result_1,
            date= row['date'],
            group_id= row['group_id']
        )
    
        
    print("CSV evaluation complete.")

if __name__ == "__main__":
    read_csv_mtgmatches()