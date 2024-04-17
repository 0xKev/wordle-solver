from wordle_solver import WordleSolver
from wordle_solver import WordleStats

import streamlit as st
import pandas as pd

# daily performance


# game mode distribution (pie chart of # of games played for each mode)

# guess distrubtion (chrat to view the number of gusses it takes for solver)

# success rate (total per game mode)

# streaks and records


# also include button that let's user pick which mode to run the bot for
# user gets to pick number of runs from 1 to 5

class WordleDashboard:
    def __init__(self, wordle_solver: WordleSolver, stats_manager: WordleStats):
        st.set_page_config(
            page_title="Wordle Solver Stats Dashboard",
            layout="centered",
            initial_sidebar_state="auto",
        )

        self.wordle_solver = wordle_solver
        self.stats_manager = stats_manager
        self.raw_data: pd.DataFrame = self.load_data()
        


    # look into caching for performance later (potential issue: cache prevents stats from updating)
    # also maybe st.fragment for auto reruns indepdently to load new data
    def load_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.stats_manager.get_file(), sep=";", header=0)
        return data

    
    def get_filter(self, game_mode: str) -> pd.DataFrame:
        return self.raw_data.filter(like=game_mode)
    
    def show_daily_stats(self):
        st.line_chart(data=self.raw_data, x="date", y="guesses")

    
    def run_app(self) -> None:
        st.title("Wordle Solver Stats Dashboard")
        

        with st.sidebar:
            menu_options = st.selectbox(
            "View stats", 
            (
                "Daily", 
                "Game Mode Distribution", 
                "Guess Distribution", 
                "Success Rate", 
                "Streaks"
                )
        )
        
        match menu_options:
            case "Daily":
                self.show_daily_stats()

            

        stats_df = self.load_data()

        st.write(stats_df)

        refresh_stats_btn = st.button("Refresh stats", key="load_data")

        if refresh_stats_btn:
            stats_df = self.load_data()

if __name__ == "__main__":
    game = WordleSolver("rand") # no param sets it to "auto"
    stats = WordleStats("stats.csv")
    dashboard = WordleDashboard(game, stats)
    dashboard.run_app()