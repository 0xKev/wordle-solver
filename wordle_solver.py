from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import ast # To eval python literals, does not execute code
import logging
import sys # to exit ------ might be unncessary
import time
from random import randint # only used to test auto play, starting random words

# Actions for letter status [incorrect, correct, present]
def action_correct(letter: str, position: int):
    """
    Action to perform when a letter is correct.

    Parameters:
    - letter: The correct letter.
    - position: The position of the letter.

    Returns:
    None
    """
    if letter not in correct_letters.get(position, []):
        correct_letters.setdefault(position, []).append(letter)

def action_absent(letter: str, position: int):
    """
    Action to perform when a letter is absent.

    Parameters:
    - letter: The absent letter.
    - position: The position of the letter.

    Returns:
    None
    """
    if letter not in incorrect_letters.get(position, []):
        incorrect_letters.setdefault(position, []).append(letter)

def action_present(letter: str, position: int):
    """
    Action to perform when a letter is present but in the wrong position.

    Parameters:
    - letter: The present letter.
    - position: The position of the letter.

    Returns:
    None
    """
    if letter not in wrong_position_letters.get(position, []):
        wrong_position_letters.setdefault(position, []).append(letter)


incorrect_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
correct_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
wrong_position_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
letter_state_action = {
    'correct': action_correct,
    'absent': action_absent,
    'present': action_present
}

def get_index_correct_letters(correct_letters: dict) -> list:
    """
    Get the index and letter of correct letters.

    Parameters:
    - correct_letters: A dictionary of correct letters.

    Returns:
    - sequences: A list of sequences of correct letters.
    """
    sequences = []
    current_sequence = []

    for index in range(len(correct_letters)):
        if correct_letters[index]:
            current_sequence.append((index, correct_letters[index][0]))
        elif current_sequence:
            sequences.append(current_sequence)
            current_sequence = []
    
    if current_sequence:
        sequences.append(current_sequence)
    
    return sequences

def solve_next_word(word_list, incorrect_letters) -> str:
    """
    Solve the next word based on the current word list and incorrect letters.

    Parameters:
    - word_list: The list of possible words.
    - incorrect_letters: A dictionary of incorrect letters.

    Returns:
    None
    """
    #print("Debug: Number of possible words before solve_next_word() = ", len(word_list))
    #print("Debug: word_list = ", word_list)

    valid_guess_wo_wrong_words = eliminate_incorrect_letters(word_list) # Eliminates incorrect letter positions
    valid_guess_correct_letters = eliminate_wo_correct_letters(valid_guess_wo_wrong_words) # Eliminates words without correct letters
    valid_guess_correct_letters_wrong_pos = eliminate_wrong_pos_letters(valid_guess_correct_letters)
    
    debug_wordlist = valid_guess_correct_letters_wrong_pos

    '''print("Debug: Number of possible words after solve_next_word() = ", len(debug_wordlist))

    if len(debug_wordlist) < 200:
        print("Possible words (valid_guess_correct_letters_wrong_pos):", debug_wordlist)'''
    print("DEBUG: Number of possible words after solve_next_word():", len(debug_wordlist))

    possible_guess = letter_frequency_rating(debug_wordlist, incorrect_letters)[1]
    print("Next possible guess:", possible_guess)
    return possible_guess
    


def eliminate_incorrect_letters(word_list) -> list:
    """
    Eliminate words that overlap with the incorrect letters.

    Parameters:
    - word_list: The list of words.

    Returns:
    - filtered_word_list: The filtered list of words.
    """
    return [word for word in word_list if not any(word[position] in incorrect_letters[position] for position in range(len(word)))]

def eliminate_wo_correct_letters(word_list) -> list:
    """
    Eliminate words without the correct letters.

    Parameters:
    - word_list: The list of words.

    Returns:
    - filtered_word_list: The filtered list of words.
    """
    filtered_word_list = []
    for word in word_list:
        all_sequence_match = True
        for seq in get_index_correct_letters(correct_letters):
            start_index = seq[0][0]
            end_index = len(seq) + start_index
            seq_letters = ''.join([letter for _, letter in seq]) # every seq is in the (index, letter) format. using _, bc index isn't used in this operation 
            if word[start_index:end_index] != seq_letters:
                all_sequence_match = False
                break
        
        if all_sequence_match:
            filtered_word_list.append(word)

    return filtered_word_list

def eliminate_wrong_pos_letters(word_list) -> list:
    """
    Eliminate words that overlap with the correct letters but in the wrong position.

    Parameters:
    - word_list: The list of words.

    Returns:
    - filtered_word_list: The filtered list of words.
    """
    filtered_word_list = []
    
    for word in word_list:
        valid_word = True
        for position, wrong_pos_letters in wrong_position_letters.items():
            if word[position] in wrong_pos_letters:
                valid_word = False
                break
            
            #if word[position] not in sum(wrong_position_letters.values(), []): # sum is used to concatenate all the lists into one list []
            required_letters = sum(wrong_position_letters.values(), [])
            if not all(letter in word for letter in required_letters):
                valid_word = False
                break
            
        
        if valid_word:
            filtered_word_list.append(word)
            
    return filtered_word_list

def letter_frequency_rating(word_list: list, incorrect_letters: list) -> tuple:
    """
    Calculate the letter frequency rating for each word in the word list.

    Parameters:
    - word_list: The list of words.
    - incorrect_letters: A dictionary of incorrect letters.

    Returns:
    - highest_word_score: A tuple containing the highest word score and the corresponding word.
    """
    letter_frequency = {
        'E' : 12.0,
        'T' : 9.10,
        'A' : 8.12,
        'O' : 7.68,
        'I' : 7.31,
        'N' : 6.95,
        'S' : 6.28,
        'R' : 6.02,
        'H' : 5.92,
        'D' : 4.32,
        'L' : 3.98,
        'U' : 2.88,
        'C' : 2.71,
        'M' : 2.61,
        'F' : 2.30,
        'Y' : 2.11,
        'W' : 2.09,
        'G' : 2.03,
        'P' : 1.82,
        'B' : 1.49,
        'V' : 1.11,
        'K' : 0.69,
        'X' : 0.17,
        'Q' : 0.11,
        'J' : 0.10,
        'Z' : 0.07 
        }

    highest_word_score = (0,)
    for word in word_list:
        word_score = 0

        for letter in set(word): # using set to prevent duplicate letters
            if letter not in sum(incorrect_letters.values(), []): # sum used with [] to concatenate all the incorrect letters into a list
                word_score += letter_frequency.get(letter.upper(), 0) # must convert lower to upper
        
        if highest_word_score[0] == 0 or word_score > highest_word_score[0]:
            highest_word_score = (word_score, word)

    return highest_word_score
  
def show_correct_answer(wordle: webdriver, correct_letters: dict) -> str:
    """
    Show the correct answer in the Wordle game.

    Parameters:
    - wordle: The webdriver instance for the Wordle game.

    Returns:
    - correct_word: The correct word.
    """
    if is_wordle_solved(correct_letters): # two methods of retrieving answer required - answer success vs answer obtained via failure is different
        return ''.join((sum(correct_letters.values(), [])))
    
    wait = WebDriverWait(wordle, 10)
    
    try:
        correct_word_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="Toast-module_toast__iiVsN"]')))
        correct_word = correct_word_element.text
    except:
        correct_word = ''.join(sum(correct_letters.values()))

    return correct_word        
    
def update_letter_status(wordle: webdriver, row: int) -> None:
    """
    Get the letter status for a given row in the Wordle game then updates letter status dictionary.

    Parameters:
    - wordle: The webdriver instance for the Wordle game.
    - row: The row number.

    Returns:
    None
    """
    WebDriverWait(wordle, 3)   
    row = wordle.find_element(By.XPATH, f'//div[@aria-label="Row {row}"]')

    # Finds the updated data-state (when it changes from tbd)
    while True:
        letter_status = row.find_elements(By.XPATH, './/div[@data-state]')

        if letter_status[4].get_attribute('data-state') != 'tbd':
            break
    
    for position, tile in enumerate(letter_status):
        letter_data_state = tile.get_attribute('data-state')
        letter = tile.text
        if letter_data_state in letter_state_action:
            if letter in correct_letters[position]:
                print('Duplicate correct: ', letter)
            
            elif letter in incorrect_letters[position]:
                print('Duplicate incorrect: ', letter)

            else:
                letter_state_action[letter_data_state](letter.lower(), position)
    

def get_words_list():
    """
    Get the list of words from a file.

    Returns:
    - word_list: The list of words.
    """
    try:
        with open('words.txt', 'r') as word_txt:

            word_txt = word_txt.read()
            word_list = ast.literal_eval(word_txt)
            
    except:
        print('File not found!')

    return word_list

def submit_guess(wordle: webdriver, letters: str):       
    """
    Submit a guess in the Wordle game.

    Parameters:
    - wordle: The webdriver instance for the Wordle game.
    - letters: The letters to guess.

    Returns:
    None
    """
    wait = WebDriverWait(wordle, 10)
    #letter_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//button[@data-key="z"]')))

    for letter in list(letters):
        wordle.find_element(By.XPATH, f'//button[@data-key="{letter}"]').click()
    
    wordle.find_element(By.XPATH, f'//button[@data-key="↵"]').click()
        
def user_guess():
    """
    Get a valid user guess.

    Returns:
    - guess: The user's guess.
    """
    while True:
        guess = input('Enter your guess (5 letters): ')
        if valid_word(guess):
            break
    
    return guess 

def valid_word(guess: str):
    """
    Check if a word is valid.

    Parameters:
    - guess: The word to check.

    Returns:
    - valid: True if the word is valid, False otherwise.
    """
    word_list = get_words_list()
    
    print('Word valid!') if guess in word_list else print('Invalid!')
    
    return guess in word_list

def test_valid_words():
    """
    Test function for valid_word().
    """
    word_list = get_words_list()

    while True:
        guess = input('Enter a word ("q" to quit): ')
        if guess == 'q':
            break
        valid_word(guess, word_list)

def is_wordle_solved(correct_letters: dict) -> bool:
    """
    Check if the Wordle puzzle is solved.

    Args:
        correct_letters (dict): The dict for correct letters.

    Returns:
        bool: True if the puzzle is solved, False otherwise.
    """

    if len(sum(correct_letters.values(), [])) == 5:
        return True
    return False
    
def startGame(mode: str = "auto") -> bool:
    """
    Start the Wordle game.

    Returns:
    True if game solved, else False
    """
    # Set the logging level to supress error messages
    logging.getLogger('selenium').setLevel(logging.CRITICAL)

    # Set the logging level to only show fatal messages
    chrome_options = Options()
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--ignore-certificate-errors")

    wordle = webdriver.Chrome(options=chrome_options)
    wordle.get('https://www.nytimes.com/games/wordle/index.html')

    wait = WebDriverWait(wordle, 5)
    
    play_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//button[@type="button"]')))
    play_button.click()

    x_button = wordle.find_element(By.XPATH, "//button[@type='button']")
    x_button.click()

    if mode == "manual":
        manual_play(wordle)
    else:
        test_auto_play(wordle)
    
    wordle_solved = is_wordle_solved(correct_letters)
    answer = show_correct_answer(wordle, correct_letters)
    
    print("The word of the day is:", answer)

    wordle.quit()
    time.sleep(1)

    return wordle_solved

def manual_play(wordle: webdriver):
    attempts = 1

    while attempts <= 6:
        if attempts != 6:
            print('This is attempt', attempts)
        guess = user_guess()
        submit_guess(wordle, guess)
        update_letter_status(wordle, attempts)
        if is_wordle_solved(correct_letters):
            print('Wordle solved!')
            break
        solve_next_word(get_words_list(), incorrect_letters)
        print()
        attempts += 1
    
    correct_answer = show_correct_answer(wordle, correct_letters)
    print('The correct word is', correct_answer)

    input("Enter any key to quit: ") # keeps selenium alive until input
  

def auto_play(wordle: webdriver):
    word_list = get_words_list()

     
    for guesses in range(1, 6): # wordle row starts from 1, not 0 based indexing
        if is_wordle_solved(correct_letters): 
            break

        else:
            guess = solve_next_word(word_list, incorrect_letters)
            time.sleep(1)
            submit_guess(wordle, guess)
            time.sleep(1)
            update_letter_status(wordle, guesses)
            

    answer = show_correct_answer(wordle, correct_letters)
    print("The answer of the day is", answer)

    input("Enter anything to quit: ")


def test_auto_play(wordle: webdriver):
    word_list = get_words_list()

     
    for guesses in range(1, 6): # wordle row starts from 1, not 0 based indexing
        if is_wordle_solved(correct_letters): 
            break

        else:
            guess = solve_next_word(word_list, incorrect_letters) if guesses != 1 else word_list[randint(0, len(word_list))]
            time.sleep(1)
            submit_guess(wordle, guess)
            time.sleep(0.75)
            update_letter_status(wordle, guesses)
            
def print_win_rate(yes: int, no: int):
    total_games_played = yes + no
    if total_games_played == 0:
        print("No games played")
        return
    print(f"Success rate {(yes / total_games_played) * 100}%")
    print(f"{yes}/{total_games_played}\n")


    
if __name__ ==  '__main__':
    yes = no = 0
    games = 1000
    
    for game in range(games):
        ##### NEED TO RESET LETTER STATUS UPON LOOPS #####
        incorrect_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
        correct_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
        wrong_position_letters = {0: [], 1: [], 2: [], 3: [], 4: []}# format as {position: letter}
        time.sleep(2)
        if startGame(): # returns True if success, else False
            yes += 1
        else:
            no += 1
        
        print_win_rate(yes, no)

        
    #word_list = get_words_list()

    #starting_guess = solve_next_word(word_list, incorrect_letters)
    