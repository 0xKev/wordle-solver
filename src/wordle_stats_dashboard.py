from wordle_solver import WordleSolver
from stats_manager import WordleStats

import streamlit as st
import pandas as pd
import time
import altair as alt
from datetime import datetime
import os

class WordleDashboard:
    def __init__(self, wordle_solver: WordleSolver, stats_manager: WordleStats):
        st.set_page_config(
            page_title="Wordle Solver Stats Dashboard",
            layout="centered",
            initial_sidebar_state="auto",
        )

        self.wordle_solver = wordle_solver
        self.stats_manager = stats_manager
        self.min_date = ""
        self.max_date = ""
        self.raw_data = ""
        
        self.load_data()

    # look into caching for performance later (potential issue: cache prevents stats from updating)
    # also maybe st.fragment for auto reruns indepdently to load new data
    def load_data(self) -> None:
        data = pd.read_csv(self.stats_manager.get_file(), sep=";", header=0)
        data["date"] = pd.to_datetime(data["date"])

        self.raw_data = data
        self.update_minMax_date()

    def data_empty(self) -> bool:
        if len(self.raw_data) == 0:
            st.warning("No data available. Please play some games to generate stats.")
            return True
        return False

    def update_minMax_date(self) -> None:
        self.min_date = self.raw_data["date"].dt.date.min()
        self.max_date = self.raw_data["date"].dt.date.max()
    
    def get_filter(self, game_mode: str, date: str = None, solved: bool = None, date_range: tuple[str, str] = None) -> pd.DataFrame:
        filtered_data = self.raw_data.copy()

        match game_mode:
            case "rand" | "auto" | "manual":
                filtered_data = filtered_data[(filtered_data["game_mode"] == game_mode)] 
            case "all":
                pass
            case _:
                raise ValueError("Game mode does not exist")
            
        if date_range:
            start_date = pd.to_datetime(date_range[0]).date()
            end_date = pd.to_datetime(date_range[1]).date()
            filtered_data = filtered_data[(filtered_data["date"].dt.date >= start_date) & (filtered_data["date"].dt.date <= end_date)]
            
        elif date:
            date = pd.to_datetime(date).date() # .date to remove trailing time
            filtered_data = filtered_data[(filtered_data["date"].dt.date == date)]

        if solved is not None:
            filtered_data = filtered_data[(filtered_data["solved"] == solved)]

        return filtered_data
    
    def show_daily_stats(self):
        if self.data_empty():
            return
        today = datetime.today().strftime("%Y-%m-%d")
        game_modes: list = self.raw_data["game_mode"].unique().tolist() + ["all"]

        solved_data = {}
        unsolved_data = {}
        data = {}

        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode, date=today)
            solved_data[mode] = self.get_filter(game_mode=mode, date=today, solved=True)
            unsolved_data[mode] = self.get_filter(game_mode=mode, date=today, solved=False)
        
        selected_mode = st.selectbox("Select game mode: ", game_modes, key=f"show_daily_stats")

        chart_data = data[selected_mode].groupby(["guesses", "solved", "answer"]).size().reset_index(name="count") # .size needed to compute # of elem per group else return obj and not actual result

        alt_chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
            alt.X("guesses:N", title="Guesses", axis=alt.Axis(labelAngle=0)), 
            alt.Y("count:Q", title="Game count", axis=alt.Axis(tickMinStep=1)),
            alt.Color("solved"),
            tooltip=["count", "guesses", "answer"],
            )
            .properties()
        )

        st.altair_chart(altair_chart=alt_chart, theme="streamlit", use_container_width=True)


    def display_sidebar(self, static: bool):
        menu_options = {
                "Daily": self.show_daily_stats, 
                "Game Mode Distribution": self.show_game_mode_dist,
                "Guess Distribution": self.show_guess_dist, 
                "Success Rate": self.show_success_rate, 
        }

        static_menu_options = {
            "Settings": self.game_settings
        }

        menu_selection = static_menu_options if static == True else menu_options

        with st.sidebar:
            selected_option = st.selectbox(
            "View stats", 
            list(menu_selection.keys()),
            key="display_sidebar()"
        )
        
        menu_selection[selected_option]()

    def display_tabs_refreshed(self) -> None:
        tab_options = {
                "Daily": self.show_daily_stats, 
                "Game Mode Distribution": self.show_game_mode_dist,
                "Guess Distribution": self.show_guess_dist, 
                "Success Rate": self.show_success_rate,
        }

        tab_names = list(tab_options.keys())

        tabs: tuple[st.tabs] = st.tabs(tabs=tab_names)

        for idx, tab in enumerate(tabs):
            with tab:
                tab_options[tab_names[idx]]()

    def show_all_stats(self):
        game_modes = self.raw_data["game_mode"].unique()

        # Create a dictionary to store the data for each game mode
        data = {}
        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode)
            data[mode]["game_number"] = range(1, len(data[mode]) + 1)

        # Create a Streamlit selectbox to choose the game mode
        selected_mode = st.selectbox("Select Game Mode", game_modes, key=f"show_all_stats_{int(time.time())}")

        data[selected_mode] = data[selected_mode].set_index("game_number")
        # Display the line graph for the selected game mode
        st.line_chart(data=data[selected_mode], y="guesses")
    
    def show_game_mode_dist(self):
        if self.data_empty():
            return
        st.subheader("Game Mode Distribution")
        game_mode_counts = self.raw_data["game_mode"].value_counts() # index = list[game modes] , values = list[counts]
        
        modes = game_mode_counts.index.tolist()
        counts = game_mode_counts.values.tolist()
        success_rates = [self.calculate_success_rate]

        chart_data = pd.DataFrame({"Modes": modes, "Counts": counts})

        alt_chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                alt.X("Modes:N", title="Game Modes", axis=alt.Axis(labelAngle=0)),
                alt.Y("Counts:Q", title="Total Guesses", axis=alt.Axis(tickMinStep=1))
            
            )
        )

        st.altair_chart(altair_chart=alt_chart, use_container_width=True)

    def show_guess_dist(self):
        if self.data_empty():
            return
        st.subheader("Total Guess Distribution")

        data = {}
        game_modes: list = self.raw_data["game_mode"].unique().tolist() + ["all"]

        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode)
        
        selected_mode = st.selectbox("Select game mode:", game_modes, key=f"show_guess_dist")

        chart_data = data[selected_mode].groupby(["guesses", "solved"]).size().reset_index(name="count")

        alt_chart = (
            alt.Chart(chart_data)
            .mark_bar()
            .encode(
                alt.X("guesses:N", title="Guesses", axis=alt.Axis(labelAngle=0)), 
                alt.Y("count:Q", title="Game count", axis=alt.Axis(tickMinStep=1)),
                alt.Color("solved")
            )
        )

        st.altair_chart(altair_chart=alt_chart, use_container_width=True)

    def show_success_rate(self):
        if self.data_empty():
            return
        st.subheader("Success Rate")

        mode_success_rates = {}
        game_modes: list = self.raw_data["game_mode"].unique().tolist()
        # displays sr for different modes and time peroids using astair graph
        
        selected_dates = st.date_input(
            "Select end date:", 
            value=(self.min_date, self.max_date), 
            min_value=self.min_date, 
            max_value=self.max_date,
            key=f"sr_date_selector"
        )

        selected_start_date = selected_dates[0].strftime("%Y-%m-%d")
        selected_end_date = selected_dates[1].strftime("%Y-%m-%d") if len(selected_dates) == 2 else selected_start_date
        
        for mode in game_modes:
            filtered_data = self.get_filter(game_mode=mode, date_range=(selected_start_date, selected_end_date))
            mode_success_rates[mode] = filtered_data

        success_rates = {}

        for mode, data in mode_success_rates.items():
            success_rates[mode] = self.calculate_success_rate(data)

        success_rate_data = pd.DataFrame(data=success_rates.items(), columns=["game_mode", "success_rate"])
        alt_chart = (
            alt.Chart(success_rate_data)
            .mark_bar()
            .encode(
                alt.X("game_mode:N", title="Game mode", axis=alt.Axis(labelAngle=0)),
                alt.Y("success_rate:Q", title="Success Rate", axis=alt.Axis(format='%', tickMinStep=1), scale=alt.Scale(domain=[0, 1])) # y axis expectes numeric values
            )
        )
            
        st.altair_chart(altair_chart=alt_chart, use_container_width=True)
    
    def calculate_success_rate(self, data_set: pd.DataFrame) -> int:
        # NOT CONVERTING TO 100 BC SHOW_SUCCESS_RATE ALT CHAR Y AXIS EXPECTS NUMERIC VALUE AND AUTO TRANSFORMS TO % 
        success: int = len(data_set[(data_set["solved"] == True)])
        fails: int = len(data_set[(data_set["solved"] == False)])
        total: int = success + fails

        return round((success / total), 2) if total != 0 else 0
        
    
def run_app() -> None:
    game = WordleSolver() # no param sets it to "auto"
    stats = WordleStats("stats.csv")
    dashboard = WordleDashboard(game, stats)

    st.title("Wordle Solver Stats Dashboard")

    dashboard.display_tabs_refreshed()

def set_working_directory() -> None:
    called_py_path = os.path.abspath(__file__)    
    py_dir = os.path.dirname(called_py_path)
    os.chdir(py_dir) 
        
if __name__ == "__main__":
    set_working_directory()
    run_app()
