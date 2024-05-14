import csv
from datetime import datetime
from pathlib import Path

class WordleStats:
    def __init__(self, filename: str):
        self.file = f"../database/{filename}" # Make sure to include .csv at end of file name
        
        self.create_headers()
    
    def create_headers(self):
        output_file = Path(self.file)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        if not output_file.exists():
            output_file.write_text("date;game_mode;answer;solved;guesses\n")

    def save_stats_csv(self, date: str, game_mode: str, answer: str, solved: bool, guesses: int):
        if self.check_valid_stats(guesses, answer):
            with open(self.file, "a", newline="") as stats_file: # unable to read with "a" append 
                writer = csv.writer(stats_file, delimiter=";")
                row_data: list = [date, game_mode, answer, solved, guesses]
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
                
    def check_valid_stats(self, guesses: int, answer: str) -> bool:
        ## 2024-05-14;rand;;False;0
        # check for invalid results - due to wordle crashes
        try:
            if answer == "" or guesses == 0:
                return False
            return True
        except:
            print(f"Result not saved due to Wordle crash.")

    def get_file(self):
        return self.file

if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d") # year-month-day
    stats = WordleStats("stats.csv")
    print(stats.create_headers()) 
    print(stats.get_file()) 
