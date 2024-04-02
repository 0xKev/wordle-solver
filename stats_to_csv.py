import csv
from datetime import datetime

"""



"""



def save_stats_csv(id: int, wordle_solved: bool, answer: str, num_guess: int, date: datetime):
    header = ["id;solved;answer;guesses;date"]

    with open("database/stats.csv", newline="") as stats_file: # unable to read with "a" append 
        stats_reader = csv.reader(stats_file)
        stats_writer = csv.writer(stats_file)

        print(type(st))

        '''if stats_reader[0] != header:
            stats_writer.writerow(header)
        
        else:
            print("header exists!")'''


if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d") # year-month-day
    save_stats_csv(10, True, "teary", 3, today)
    