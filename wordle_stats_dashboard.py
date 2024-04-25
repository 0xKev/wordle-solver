from wordle_solver import WordleSolver
from wordle_solver import WordleStats

import streamlit as st
import pandas as pd
import time
import altair as alt
from datetime import datetime
from datetime import time as time_class

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
        st.session_state.queued_game = False
        st.session_state.game_freq = 1
        st.session_state.active_game = False
        self.scheduled_time = None
        
        self.load_data()

    # look into caching for performance later (potential issue: cache prevents stats from updating)
    # also maybe st.fragment for auto reruns indepdently to load new data
    def load_data(self) -> None:
        data = pd.read_csv(self.stats_manager.get_file(), sep=";", header=0)
        data["date"] = pd.to_datetime(data["date"])

        self.raw_data = data
        self.update_minMax_date()
        

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
        today = datetime.today().strftime("%Y-%m-%d")
        game_modes: list = self.raw_data["game_mode"].unique().tolist() + ["all"]

        solved_data = {}
        unsolved_data = {}
        data = {}

        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode, date=today)
            solved_data[mode] = self.get_filter(game_mode=mode, date=today, solved=True)
            unsolved_data[mode] = self.get_filter(game_mode=mode, date=today, solved=False)
        
        selected_mode = st.selectbox("Select game mode: ", game_modes, key=f"show_daily_stats__{int(time.time())}")

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

        # ALSO DISPLAY SR

    def display_sidebar(self, static: bool):
        menu_options = {
                "Daily": self.show_daily_stats, 
                "Game Mode Distribution": self.show_game_mode_dist,
                "Guess Distribution": self.show_guess_dist, 
                "Success Rate": self.show_success_rate, 
                "Streaks": self.show_streaks,
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
                "Streaks": self.show_streaks,
        }

        tab_names = list(tab_options.keys())

        tabs: tuple[st.tabs] = st.tabs(tabs=tab_names)

        for idx, tab in enumerate(tabs):
            with tab:
                tab_options[tab_names[idx]]()
    
    def display_sidebar_non_refreshed(self) -> None:
        menu_options = {
            "Settings": self.game_settings
        }

        with st.sidebar:
            selected_option = {}

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
        st.subheader("Total Guess Distribution")

        data = {}
        game_modes: list = self.raw_data["game_mode"].unique().tolist() + ["all"]

        for mode in game_modes:
            data[mode] = self.get_filter(game_mode=mode)
        
        selected_mode = st.selectbox("Select game mode:", game_modes, key=f"show_guess_dist_{int(time.time())}")

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
        st.subheader("Success Rate")

        mode_success_rates = {}
        game_modes: list = self.raw_data["game_mode"].unique().tolist()
        # displays sr for different modes and time peroids using astair graph
        
        selected_dates = st.date_input(
            "Select end date:", 
            value=(self.min_date, self.max_date), 
            min_value=self.min_date, 
            max_value=self.max_date,
            key=f"sr_date_selector_{int(time.time())}"
        )

        selected_start_date = selected_dates[0].strftime("%Y-%m-%d")
        selected_end_date = selected_dates[1].strftime("%Y-%m-%d") if len(selected_dates) == 2 else selected_start_date
        
        #selected_mode = st.selectbox("Choose a game mode:", game_modes)

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
                alt.Y("success_rate:Q", title="Success Rate", axis=alt.Axis(format='%', tickMinStep=1)) # y axis expectes numeric values
            )
        )
        #st.write(f"{selected_mode} sr: {success_rates[selected_mode]}")

            
        st.altair_chart(altair_chart=alt_chart, use_container_width=True)
    
    def calculate_success_rate(self, data_set: pd.DataFrame) -> int:
        # NOT CONVERTING TO 100 BC SHOW_SUCCESS_RATE ALT CHAR Y AXIS EXPECTS NUMERIC VALUE AND AUTO TRANSFORMS TO % 
        success: int = len(data_set[(data_set["solved"] == True)])
        fails: int = len(data_set[(data_set["solved"] == False)])
        total: int = success + fails

        return round((success / total), 2) if fails != 0 else 1
        
        

    def show_streaks(self):
        st.subheader("Streaks!")
        longest_streak = 0
        
        filtered_data = self.raw_data[self.raw_data["solved"]] # able to use boolean indexing bc "solved" values are True or False
        data = self.raw_data
        # .transform works on each group and "idxmax" returns the first index of the maximum value (True).
        # so each group of solved dates is assigned the idx of the first True in each group and finally compared to the original idx
        # if match with original idx then condition True, row is the first win for each date group
        daily_first_win = filtered_data.groupby(filtered_data["date"].dt.date)["solved"].transform("idxmax") == filtered_data.index
        data["daily_first_win"] = daily_first_win.reindex(data.index).fillna(False) # to fill in N/A with False for fail answers
        data["daily_first_win"] = data["daily_first_win"].infer_objects(copy=False) # fillna deprecated and will change in the future

        filtered_daily_wins = data[data["daily_first_win"]]

        # create column showing # of days diff
        filtered_daily_wins["diff"] = filtered_daily_wins["date"].diff().dt.days

        # create column to mark the days where diff == 1
        filtered_daily_wins["consecutive"] = filtered_daily_wins["diff"] == 1

        filtered_daily_wins["streak_count"] = filtered_daily_wins["consecutive"].cumsum()

        streak_count = filtered_daily_wins.groupby("date")["diff"].size()

        consecutive_days = filtered_daily_wins.groupby("streak_count").size().max()

        st.write(consecutive_days + 1)

    def toggle_play_enabled(self) -> None:
        st.session_state.play_enabled = not st.session_state.play_enabled

    def game_settings(self) -> None:
        if "play_enabled" not in st.session_state:
            st.session_state.play_enabled = False

        schedule_col, manual_col = st.columns(2)

        with st.expander("Schedule game:"):
            freq = st.number_input(
                label="Select :blue[duration] in between games:sunglasses:",
                value=1,
                min_value=1,
                max_value=24,
                key=f"game_schedule_{int(time.time())}",
                step=1,
                on_change=self.schedule_slider_moved,
                disabled=st.session_state.get("slider_moved", False) or st.session_state.active_game
            )

            st.session_state.queued_game = True
            st.session_state.game_freq = freq
            
        with schedule_col:
            with st.form(key=f"game_schedule_form_{int(time.time())}"):
                st.write("Schedule game:")
                current_scheduled_time = time_class(hour=20) if not self.scheduled_time else self.scheduled_time
                time_val = st.time_input("Select :blue[time] for automatic Wordle games:sunglasses:", value=current_scheduled_time)

                self.scheduled_time = time_val

                submitted = st.form_submit_button("Set time")
                if submitted:
                    st.write(f"time val is {time_val}\nsession state schedule time is {self.scheduled_time}")

            
        manual_toggle = st.toggle(
            "Activate manual play", 
            key=f"manual_toggle", 
            value=Falsewo, 
            on_change=self.toggle_play_enabled()
        )
        
        with manual_col:
            with st.form(key=f"game_settings_{int(time.time())}"):

                game_mode = st.radio(
                    "Select game mode",
                    ["Random", "Auto"],
                    captions=["random first guess", "optimized first guess"],
                    disabled=not st.session_state.play_enabled,
                    key=f"game_mode_{int(time.time())}"
                )

                submitted = st.form_submit_button("Play game", disabled=not st.session_state.play_enabled)
                

    def schedule_slider_moved(self) -> None:
        st.session_state.slider_moved = True
        self.check_session_game()

    def check_session_game(self):
        if st.session_state.queued_game and not st.session_state.active_game:
            self.run_games(st.session_state.game_freq)


    def run_games(self, num_games: int = 1) -> None:
        try:
            for _ in range(num_games):
                st.session_state.active_game = True
                self.wordle_solver.startGame()
                results = self.wordle_solver.get_results()
                self.stats_manager.save_stats_csv(*results)
                st.success("Game completed and stats saved!")
        except:
            st.warning("Wordle solver crashed")
            st.rerun()
        finally:
            st.session_state.game_freq = False
            st.session_state.queued_game = False
    
    def reset_game_session(self):
        if st.button("Click to reset game sessions to False", disabled=False):
            st.session_state.queued_game = False
            st.session_state.active_game = False

    # sessino state saves freq and if game active
    # schedule based off freq and only play if session state not active

def run_app() -> None:
    game = WordleSolver("rand") # no param sets it to "auto"
    stats = WordleStats("stats.csv")
    dashboard = WordleDashboard(game, stats)

    st.title("Wordle Solver Stats Dashboard")
    dashboard.reset_game_session()
    dashboard.game_settings()
    placeholder = st.empty()

    while not True:
        dashboard.load_data()
        with placeholder.container():
            dashboard.display_tabs_refreshed()
        time.sleep(2)

    dashboard.load_data()
    dashboard.display_tabs_refreshed()

      
    
# no need for loop refresh
# only refresh if game has been played, make sure to use the st.warning if ailed and success
# also only auto refresh on set time ffter game played
# might need set a flag to determine if game ha sjust been played
        
        
                


if __name__ == "__main__":
    run_app()
