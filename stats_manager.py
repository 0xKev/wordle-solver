import csv
from datetime import datetime

class WordleStats:
    def __init__(self, filename: str):
        self.filename = f"database/{filename}" # Make sure to include .csv at end of file name
        # create headers along with init
        # game mode, date, success or fail, word answer, 

        self.create_headers()
    
    # "x" creates file and opens to write, use "x" when done but ""
    def create_headers(self):
        try:
            with open(self.filename, "x", newline="") as stats_file:
                writer = csv.writer(stats_file)
                writer.writerow(["date;game_mode;answer;solved;guesses"])
        except FileExistsError:
            print(f"File exists: {self.filename}")
    
    def save_stats_csv(self, date: str, game_mode: str, answer: str, solved: bool, guesses: int):
        with open("database/stats.csv", "a+", newline="") as stats_file: # unable to read with "a" append 
            writer = csv.writer(stats_file)
            row_data: list = [f"{date};{game_mode};{answer};{solved};{guesses}"]
            writer.writerow(row_data)


        
            


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d") # year-month-day
    stats = WordleStats("stats.csv")    