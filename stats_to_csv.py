import csv
from datetime import datetime

def save_stats_csv(id: int, wordle_solved: bool, answer: str, num_guess: int, date: datetime):
    header = ["id;solved;answer;guesses;date"]

    with open("database/stats.csv", "a", newline = "") as stats_file:
        stats_writer = csv.writer(stats_file)
        stats_reader = csv.reader(stats_file)

        for line in stats_reader:
            print(line)

if __name__ == "__main__":
    today = datetime.today().strftime("%Y-%m-%d")
    save_stats_csv(10, True, "teary", 3, today)
    print(today)