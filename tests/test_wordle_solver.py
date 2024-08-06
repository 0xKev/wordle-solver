import sys

sys.path.append("../")

from src.wordle_solver import WordleSolver
from src.stats_manager import WordleStats

if __name__ == "__main__":

    game = WordleSolver() # no param sets it to "auto"
    stats = WordleStats("stats.csv")
    for i in range(100):
        game.startGame("rand")
        results: list = game.get_results()
        print(results)
        stats.save_stats_csv(*results)
        print("--- Stats saved ---")