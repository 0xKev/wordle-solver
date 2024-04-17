from wordle_solver import WordleSolver
from wordle_solver import WordleStats

import streamlit as st
import pandas as pd
from datetime import datetime

# daily performance


# game mode distribution (pie chart of # of games played for each mode)

# guess distrubtion (chrat to view the number of gusses it takes for solver)

# success rate (total per game mode)

# streaks and records


# also include button that let"s user pick which mode to run the bot for
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
        data["date"] = pd.to_datetime(data["date"])
        return data

    
    def get_filter(self, game_mode: str, date: str = None) -> pd.DataFrame:
        if date:
            date = pd.to_datetime(date).date() # .date to remove trailing time
            match game_mode:
                case "rand" | "auto" | "manual":
                    return self.raw_data[(self.raw_data["game_mode"] == game_mode) & (self.raw_data["date"].dt.date == date)] 
                case "all":
                    return self.raw_data[self.raw_data["date"].dt.date == date]
                case _:
                    raise "Game mode does not exist"

        return self.raw_data[self.raw_data["game_mode"] == game_mode]
    
    def show_daily_stats(self):
        today = datetime.today().strftime("%Y-%m-%d")
        game_modes: list = self.raw_data["game_mode"].unique()

        data = {}

        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode, date=today)
            data[mode]["game_number"] = range(1, len(data[mode]) + 1)

        selected_mode = st.selectbox("Select game mode: ", game_modes)

        st.line_chart(data=data[selected_mode], x="game_number", y="guesses")

    def show_all_stats(self):
        game_modes = self.raw_data["game_mode"].unique()

        # Create a dictionary to store the data for each game mode
        data = {}
        for mode in game_modes:
            data[mode] = self.raw_data[self.raw_data["game_mode"] == mode]
            data[mode]["game_number"] = range(1, len(data[mode]) + 1)

        # Create a Streamlit selectbox to choose the game mode
        selected_mode = st.selectbox("Select Game Mode", game_modes)

        data[selected_mode].set_index("game_number")
        # Display the line graph for the selected game mode
        st.line_chart(data=data[selected_mode], x="game_number", y="guesses")

    
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