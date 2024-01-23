# Wordle-solver #
Python program that helps you solve the daily Wordle puzzle by giving you the next best word to guess.

# Usage #

Make sure you're using Python3.
Run the below command in your Terminal:


```
python wordle-solver.py
```
or
```
python3 wordle-solver.py
```

After running <code style="color: gold">wordle-solver.py</code>, a selenium browser will open to Wordle:

![Wordle Selenium Default](/images/wordle-selenium.PNG?raw=true "Wordle Selenium")

Enter your guesses within your terminal:

![Input Guess](/images/first-guess.PNG?raw=true "Input Guess Image")

Your guesses will be reflected upon the selenium Wordle window:

![Wordle Selenium First Guess](/images/wordle-word-guessed.PNG?raw=true "Wordle Selenium First Guess")

Your terminal will then update with the next best guess:

![Solve Next Word](/images/suggested_guess.PNG "Next Best Word")

Repeat above steps until Wordle is solved.

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
git clone https://github.com/0xKev/wordle-solver
```
2. Move into wordle-solver directory
```
cd wordle-solver/
```
3. Install required packages via pip
```
pip install -r requirements.txt
```

# To Do #
With no particular timeframe:
- [ ] Clean up code 
- [ ] Add wordle-solver stat tracker
- [ ] Add automatic mode without user input
