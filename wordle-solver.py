import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import ast # To eval python literals, does not execute code
import logging


# Actions for letter status [incorrect, correct, present]
def action_correct(letter: str, position: int):
    if letter not in correct_letters.get(position, []):
        correct_letters.setdefault(position, []).append(letter)

def action_absent(letter: str, position: int):
    if letter not in incorrect_letters.get(position, []):
        incorrect_letters.setdefault(position, []).append(letter)

def action_present(letter: str, position: int):
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

def get_index_correct_letters(correct_letters) -> list:
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

def solve_next_word(incorrect_letters: dict, correct_letters: dict, wrong_position_letters: dict, word_list):
    print("Debug: Number of possible words before solve_next_word() = ", len(word_list))
    #print("Debug: word_list = ", word_list)

    valid_guess_wo_wrong_words = eliminate_incorrect_letters(word_list) # Eliminates incorrect letter positions
    valid_guess_w_correct_letters = eliminate_wo_correct_letters(valid_guess_wo_wrong_words) # Eliminates words without correct letters
    #valid_guess_correct_letters_wrong_pos = finetune_valid_guesses(valid_guess_w_correct_letters)

    print("Debug: Number of possible words after solve_next_word() = ", len(valid_guess_w_correct_letters))
    if len(valid_guess_w_correct_letters) < 50:
        print("Possible words:", valid_guess_w_correct_letters)


def eliminate_incorrect_letters(word_list) -> list:
    return [word for word in word_list if not any(word[position] in incorrect_letters[position] for position in range(len(word)))]

def eliminate_wo_correct_letters(word_list) -> list:
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

def show_correct_answer(wordle: webdriver):
    
    wait = WebDriverWait(wordle, 10)
    
    #exit_stats_element = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@class="Modal-module_closeIconButton__y9b6c"]')))
    #exit_stats_element.click()
    
    correct_word_element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="Toast-module_toast__iiVsN"]')))
    correct_word = correct_word_element.text
    #//div[@class="Toast-module_toast__iiVsN"]
    

    return correct_word
    
'''def finetune_valid_guesses(word_list) -> list:
    filtered_word_list = []
    for word in word_list:
        for position, letter in enumerate(wrong_position_letters):
            if word[position] not in wrong_position_letters[position]:
                pass'''
                
                

'''
# could be useful for correct but wrong pos words so saving this for now
def eliminate_wo_correct_letters(word_list) -> list:
    highest_word_value = 0
    filtered_word_list = []
    for word in word_list:
        word_value = 0
        for position, letter in enumerate(word):
            if letter in correct_letters[position]:
                word_value += 1
        highest_word_value = word_value
        if word_value >= highest_word_value:
            filtered_word_list.append(word)
    
    return filtered_word_list'''
    

def get_letter_status(wordle: webdriver, row: int):
    WebDriverWait(wordle, 3)   
    row = wordle.find_element(By.XPATH, f'//div[@aria-label="Row {row}"]')

    # Finds the updated data-state (when it changes from tbd)
    while True:
        letter_status = row.find_elements(By.XPATH, './/div[@data-state]')

        if letter_status[4].get_attribute('data-state') != 'tbd':
            break
    
    for position, tile in enumerate(letter_status): # Removed start = 1 so it's easier to work with solve_next_word
        letter_data_state = tile.get_attribute('data-state')
        letter = tile.text
        #letters_in_incorrect_set = {letter[0] for letter in incorrect_letters}
        #letters_in_correct_set = {letter[0] for letter in correct_letters}
        #print(letter) # debug
        print(f'get letter status: {letter}, {letter_data_state}') # debug
        if letter_data_state in letter_state_action:
            if letter in correct_letters[position]:
                print('Duplicate correct: ', letter) # debug
                #correct_letters[position].append(letter)
            
            elif letter in incorrect_letters[position]:
                print('Duplicate incorrect: ', letter)
                #incorrect_letters[position].append(letter)

            else:
                letter_state_action[letter_data_state](letter.lower(), position)
                #letter_state_action[letter_data_state](letter, position) # only used for new letters!!! this is rewriting the results before causing issues
            #print('condition activates') # debug
    
    print('correct letters: ', correct_letters)
    print('wrong position letters:', wrong_position_letters)
    print('incorrect_letters:', incorrect_letters)

def get_words_list():
    try:
        with open('words.txt', 'r') as word_txt:

            word_txt = word_txt.read()
            word_list = ast.literal_eval(word_txt)
            
    except:
        print('File not found!')

    return word_list

def submit_guess(wordle: webdriver, letters: str):       
    wait = WebDriverWait(wordle, 10)
    letter_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//button[@data-key="z"]')))

    for letter in list(letters): #To iterate over the letters 
        print(f'submit_guess function debug: {letter}')
        #letter_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//button[@data-key="{letter}"]')))
        wordle.find_element(By.XPATH, f'//button[@data-key="{letter}"]').click()
        #letter_button.click()
    
    wordle.find_element(By.XPATH, f'//button[@data-key="↵"]').click()
        
def user_guess():
    guess = ''
    while not valid_word(guess):

        guess = input('Enter your word: ')
    
    return guess if valid_word(guess) else False

def valid_word(guess: str):
    word_list = get_words_list()
    
    print('Word valid!') if guess in word_list else print('Invalid!')
    
    return guess in word_list

def startGame():
    attempts = 0
    #guess = user_guess()

    # Set the logging level to supress error messages
    logging.getLogger('selenium').setLevel(logging.CRITICAL)

    # Set the logging level to only show fatal messages
    chrome_options = Options()
    chrome_options.add_argument('--log-level=3')

    wordle = webdriver.Chrome(options=chrome_options)
    wordle.get('https://www.nytimes.com/games/wordle/index.html')

    wait = WebDriverWait(wordle, 5)
    
    play_button = wait.until(EC.presence_of_element_located((By.XPATH, f'//button[@type="button"]')))
    play_button.click()

    x_button = wordle.find_element(By.XPATH, "//button[@type='button']")
    x_button.click()

    
    '''submit_guess(wordle, guess, attempts)

    wordle.implicitly_wait(10)
    get_letter_status(wordle, guess)'''
    manual_play(wordle)
    
    keep_alive = input('Submit any key to quit.')

def manual_play(wordle: webdriver):
    attempts = 1

    while attempts <= 6:
        if attempts != 6:
            print('This is attempt', attempts)
        guess = user_guess()
        submit_guess(wordle, guess)
        get_letter_status(wordle, attempts)
        solve_next_word(incorrect_letters, correct_letters, wrong_position_letters, get_words_list())
        print()
        attempts += 1

    print('Final attempt (6)')   
    
    correct_answer = show_correct_answer(wordle)
    print('The correct word is', correct_answer)
    input()

def test_valid_words():
    word_list = get_words_list()

    while True:
        guess = input('Enter a word ("q" to quit): ')
        if guess == 'q':
            break
        valid_word(guess, word_list)
    
if __name__ ==  '__main__':
    word = ''
    startGame()
    #get_source_code()
    #testing()
    #print(take_guess())
    '''while word != 'q':
        word = input('enter a word: ')
        valid_word(word)'''
    