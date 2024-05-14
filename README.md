# Wordle-solver #
Python program that helps you solve the daily Wordle puzzle by giving you the next best word to guess. The solver offers three game modes: manual, auto, and rand. You can use the solver directly from the terminal or launch a dashboard for additional features and statistics.

# Table Of Content
- [Getting Started](#getting-started)
- [Command Line Usage](#command-line)
- [Dashboard](#dashboard)
- [Examples](#examples)


# Usage #
### Command Line ### 
To use the Wordle solver from the command line, run the <code style="color:gold">wordle_solver.py</code> script with the desired game mode:

`python wordle_solver.py [-h] --mode [manual|auto|rand] [--browser]`


- [`manual`](#manual-mode): Play the game manually by entering your guesses.
- [`auto`](#auto--random-mode): Let the solver automatically play the game, starting with the best word determined by the algorithm.
- [`rand`](#auto--random-mode): Let the solver automatically play the game with a random first guess.


The `--browser` flag controls whether a selenium window is displayed or runs in headless mode.
- If the `--browser` flag is not used (default) then the solver will run in headless mode. Results will be shown in the terminal without a visible browser window.
- If the `--browser` flag is used, then the solver will display the active selenium window so you can watch as the solver solves the game live.

The `-h` flag will display the help message and explain each flag.

After each game, the solve will save your game stats to `database/stats.csv`. This file will be automatically created if it does not exist.

### Dashboard ###

To launch the dashboard and access additional features and statistics:


```
python -m streamlit run wordle_stats_dashboard.py
```
![Wordle Dashboard](/images/dashboard/stats-dashboard.png?raw=True "Stats Dashboard")

## Examples

### Manual Mode
`python wordle-solver.py --mode manual --browser`
#### `--browser` flag opens Selenium browser window (optional)

![Wordle Selenium Default](/images/game_modes/manual/wordle-selenium.PNG?raw=true "Wordle Selenium")

Enter your guesses within your terminal:

![Input Guess](/images/game_modes/manual/first-guess.PNG?raw=true "Input Guess Image")

Your guesses will be reflected upon the selenium Wordle window:

![Wordle Selenium First Guess](/images/game_modes/manual/wordle-word-guessed.PNG?raw=true "Wordle Selenium First Guess")

Your terminal will then update with the next best guess:

![Solve Next Word](/images/game_modes/manual/suggested_guess.PNG "Next Best Word")

Repeat above steps until Wordle is solved.

![Wordle Solved](/images/terminal/wordle-solved.png "Wordle Solved")

### Auto / Random Mode

`python wordle-solver.py --mode [manual|auto] --browser`

![Auto Solve](/images/game_modes/rand_auto/solver-mode.png "Auto Solve")

Watch as the solver automatically solves Wordle for you. 
Results will also be shown in the terminal.

![Wordle Result](/images/terminal/wordle-solved.png "Wordle Result Terminal")


# Getting Started #

## Prerequisites ##

- https://sites.google.com/chromium.org/driver/downloads (The latest version is fine)
- pip (Make sure you are using Python3)
    ```
    python -m ensurepip --upgrade
    ```

## Installation ##
1. Clone the repo
```
git clone https://github.com/0xKev/wordle-solver.git
```
2. Move into wordle-solver directory
```
cd wordle-solver/
```
3. Install required packages via pip
```
pip install -r requirements.txt
```
4. Move into the src/ directory:
```
cd src/
```
### [Jump to usage](#usage)