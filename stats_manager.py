import csv
from datetime import datetime
import pandas as pd

class WordleStats:
    def __init__(self, filename: str):
        self.file = f"database/{filename}" # Make sure to include .csv at end of file name
        # create headers along with init
        # game mode, date, success or fail, word answer, 

        self.create_headers()
    
    # "x" creates file and opens to write, use "x" when done but ""
    def create_headers(self):
        try:
            with open(self.file, "x", newline="") as stats_file:
                writer = csv.writer(stats_file)
                writer.writerow(["date;game_mode;answer;solved;guesses"])
        except FileExistsError:
            print(f"File exists: {self.file}")
    
    def save_stats_csv(self, date: str, game_mode: str, answer: str, solved: bool, guesses: int):
        with open(self.file, "a+", newline="") as stats_file: # unable to read with "a" append 
            writer = csv.writer(stats_file)
            row_data: list = [f"{date};{game_mode};{answer};{solved};{guesses}"]
            writer.writerow(row_data)

    def get_answer(self, date: str = None) -> str:
        with open(self.file, "r", newline="") as stats_file:
            reader = csv.reader(stats_file, delimiter=";")
            next(reader)
            for row in reader:
                if date:
                    if row[0] == date:
                        return row[2]
                else:
                    return row[2]

    def get_file(self):
        return self.file
 


        
            


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d") # year-month-day
    stats = WordleStats("stats.csv")   
    print(stats.get_file()) 