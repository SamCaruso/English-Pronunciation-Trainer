"""
English Pronunciation Trainer

This console-based app helps the user understand and memorise the most common 
spelling-pronunciation patterns of English phonemes(=sounds).

Overview:
    1.Requires previous technical knowledge of pronunciation and it is based on Standard BRITISH ENGLISH.
    2.Checks for an internet connection:
        -Plays audio retrieved through the Free Dictionary API if online.
        -Marks audio 'offline' and continues.
        -Updates audio status when the connection is restored.
    3.Downloads audio file into a local directory if audio is available. 
    4.Introduces one new sound at a time and shows its most common spelling patterns with examples.
    5.Offers randomised spelling exercises.
    6.Drills homophones.

Features:
    1.Progress is saved to a JSON file for future review and to avoid repetition.
    2.Only 1 new phoneme can be studied per session to promote gradual learning.
    3.Compulsory review of previously studied phonemes at the beginning of each session.
    3.The dictionary 'phonemes' and all its content are manually curated to ensure accuracy.
    4.If the Free Dictionary API doesn't provide the BRITISH ENGLISH version of the phoneme, it handles missing audio gracefully.

Modules:
1. main : core exercises and review. 
2. phoneme_api : handling of the Free Dictionary API to reproduce the sound of phonemes if available. """

import random
from phoneme_api import get_phoneme
import json
import time
from pathlib import Path
import log_file
import logging
from playsound import playsound
import requests

logger = logging.getLogger(__name__)

file_path = Path(__file__).parent / 'English_Pronunciation_Trainer.json'

phonemes = {
    '/ɔ:/': {
        'patterns': {
            'aw': ('saw', 'yawn', 'draw'),
            'ore': ('core', 'snore', 'before'),
            'oar': ('board', 'coarse', 'soar'),
            'or': ('port', 'absorb', 'corn'),
            'au': ('august', 'autumn', 'flaunt'),
            'oor': ('door', 'floor', 'poor'),
            'our': ('mourn', 'pour', 'four'),
            'war': ('war', 'award', 'swarm'),
        },
        'spelling': {
            "/'ɔ:də/": ('order', 'aurder', 'awder'),
            "/'kɔ:ʃən/": ('caution', 'courtion', 'coretion'),
            '/wɔ:d/': ('ward', 'word', 'woard'),
            '/lɔ:ntʃ/': ('launch', 'lunch', 'lawnch'),
            '/dɔ:n/': ('dawn', 'down', 'daun'),
            '/dʒɔ:/': ('jaw', 'jore', 'joor'),
            "/dɪ'vɔ:s/": ('divorce', 'divauce', 'divawrce'),
            "/ə'fɔ:d/": ('afford', 'affawd', 'affaud'),
            '/stɔ:/': ('store', 'stoar', 'stour'),
            '/swɔ:/': ('swore', 'swar', 'swor'),
        },
        'homophones': {
            '/ɔ:/': {'or', 'oar', 'awe', 'ore'},
            '/sɔ:/': {'saw', 'sore', 'soar'},
            '/bɔ:d/': {'bored', 'board'},
            '/flɔ:/': {'floor', 'flaw'},
            '/ʃɔ:/': {'shore', 'sure'},
            '/pɔ:/': {'poor', 'paw', 'pore', 'pour'},
            '/sɔ:s/': {'sauce', 'source'},
            "/'mɔ:nɪŋ/": {'morning', 'mourning'},
            '/stɔ:k/': {'stalk', 'stork'},
            '/wɔ:/': {'war', 'wore'},
        },
        'api': 'or'
    },
    '/ɜ:/': {
        'patterns': {
            'er + con': ('alert', 'deserve', 'universe'),
            'ir + con': ('girl', 'third', 'dirt'),
            'wor + con': ('word', 'work', 'worse'),
            'ur + con': ('curl', 'burden', 'lurk'),
            'ear + con': ('pearl', 'hearse', 'learn'),
        },
        'spelling': {
            '/wɜ:m/': ('worm', 'warm', 'werm'),
            '/ʃɜ:t/': ('shirt', 'shert', 'short'),
            '/bɜ:st/': ('burst', 'birst', 'berst'),
            '/pɜ:k/': ('perk', 'purk', 'pirk'),
            '/fɜ:m/': ('firm', 'furm', 'ferm'),
        },
        'homophones': {
            '/hɜ:d/': {'heard', 'herd'},
            '/fɜ:/': {'fir', 'fur'},
            '/wɜ:d/': {'word', 'whirred'},
            '/kɜ:b/': {'kerb', 'curb'},
        },
        'api': 'err'
    },
    '/eə/': {
        'patterns': {
            'are': ('care', 'stare', 'ware'),
            'air': ('affair', 'chair', 'repair'),
            'ear': ('swear', 'pear', 'bear'),
        },
        'spelling': {
            '/leə/': ('lair', 'lare', 'lere'),
            '/preə/': ('prayer', 'prarre', 'prair'),
            "/ˌvedʒə'teəriən/": ('vegetarian', 'vegetearian', 'vegetairian'),
            "/'peərənt/": ('parent', 'pairent', 'perent'),
            "/'veəri/": ('vary', 'very', 'veary'),
        },
        'homophones': {
            '/feə/': {'fair', 'fare'},
            '/peə/': {'pare', 'pair', 'pear'},
            '/heə/': {'hair', 'hare'},
            '/steə/': {'stare', 'stair'},
            '/fleə/': {'flair', 'flare'},
        },
        'api': 'air'
    },
    '/i:/': {
        'patterns': {
            'ee': ('green', 'proceed', 'tree'),
            'ie': ('believe', 'grief', 'priest'),
            'ea': ('each', 'bleak', 'dream'),
            'e.e': ('complete', 'phoneme', 'theme'),
            'i.e': ('police', 'prestige', 'unique'),
        },
        'spelling': {
            '/tʃi:t/': ('cheat', 'cheet', 'chete'),
            "/ə'tʃi:v/": ('achieve', 'acheive', 'achive'),
            '/fli:t/': ('fleet', 'fleat', 'fliet'),
            "/kən'si:t/": ('conceit', 'conciet', 'concete'),
            '/pli:/': ('plea', 'plee', 'ply'),
        },
        'homophones': {
            '/si:/': {'sea', 'see'},
            '/pi:': {'pea', 'pee'},
            '/bi:t/': {'beet', 'beat'},
            '/bi:/': {'bee', 'be'},
            '/ri:d/':{'read', 'reed'},
            '/si:m/': {'seam', 'seem'},
            '/fli:/': {'flee', 'flea'},
        },
        'api': 'e'
    }
}

def online():
    """Checks for an internet connection as it affects how the app behaves. 

    Returns:
        bool: True if connection exists, False if not.
    """
    try:
        requests.head("https://www.google.com", timeout=3)
        logger.info('Accessed internet connection')
        return True
    except requests.RequestException:
        logger.error('No internet connection')
        return False
    
        
def learn(phoneme):
    """Play sound of phoneme if available through the 'get_phoneme()' API and show its commom spelling patterns.

    Args:
        phoneme (str): Phoneme randomly picked from the 'phonemes' dictionary.

    Returns:
        str | None:
            - Path to downloaded file if available.
            - 'offline' if there is no internet connection.
            - None if audio is unavailable or an error occurred.
    """

    print(f'New phoneme = {phoneme}\n')
    if online():
        audio = get_phoneme(phonemes[phoneme]['api'])
        if audio:
            playsound(audio)
            logger.info(f'Successful reproduction of {phoneme}')
        else:
            print('Audio unavailable\n')
    else:
        audio = 'offline'
        logger.info(f"learn() returns 'offline'")
    print('The most common spelling patterns for this phoneme are: \n')

    for pattern, example in phonemes[phoneme]['patterns'].items():
        examples = ', '.join(random.sample(example, k = 2))
        print(f'{pattern.upper()} -> {examples}')
    return audio
        

def spell(phoneme, audio):
    """If the sound is available through the 'get_phoneme()' API, there is a chance to listen to it again, before starting the spelling tests for the target phoneme.

    Args:
        phoneme (str): Phoneme being studied.
        audio (str | None):
            - Path to downloaded file if available.
            - 'offline' if there is no internet connection.
            - None if audio is unavailable or an error occurred.
    """
    if audio and audio != 'offline':
        while True:
            ask = input('Do you want to listen to the phoneme one more time before we start? (y/n): ').lower().strip()
            if ask == 'y':
                playsound(audio)
                break
            elif ask == 'n':
                break
            else:
                print('Invalid entry. Only y/n')
            
    words = random.sample(list(phonemes[phoneme]['spelling']), k = 5)
    
    spell_tests(words, phoneme)

    
def spell_tests(words_list, phoneme):
    """For each word to learn, 'test_no_help()' first and 'test_with_help()' after if needed.

    Args:
        words_list (list): Random selection of words to test.
        phoneme (str): Phoneme being studied.
    """
    retry = []
    print('\nWrite the word that corresponds to the following phonemes. You have 5 attempts')
    
    for index, word in enumerate(words_list):
        print(f'{index + 1}. How do you spell {word}?')
        test_no_help(word, retry, phoneme)
    
    if retry:
        for word in retry:
            test_with_help(word, phoneme)
                
    
def test_no_help(word, retry_list, phoneme):
    """Test spelling knowledge without any help.
    
    5 attempts to pass the correct spelling of the word, which is the first element of the relative tuple in the 'phonemes' dictionary. 
    After 5 failed attempts, the word is appended to a 'retry_list' for future furher testing.

    Args:
        word (str): Phonemic transcription of the word we need to guess the spelling of.
        retry_list (list): List containing words not guessed after 5 attempts.
        phoneme (str): Phoneme being studied.
    """
    attempts = 5
    while attempts > 0:
        answer = input(f'{attempts}. ').lower().strip()
        solution = phonemes[phoneme]['spelling'][word][0]
        if answer == solution:
            print('Yes!\n')
            return
        if not answer.isalpha():
            print('Only letters')
            continue
        else:
            attempts -= 1
    retry_list.append(word)
    print()
  
    
def test_with_help(word, phoneme):
    """Test spelling with the help of prompts.
    
    If words are not correctly guessed in 'test_no_help()', they are tested here through the choice between the 3 prompts contained in the relative tuples in the 'phonemes' dictionary. 
    Only those 3 words are allowed as answers. If the attempts fail, the solution is given by the app.

    Args:
        word (str): Phonemic transcription of the word we need to guess the spelling of.
        phoneme (str): Phoneme being studied.
    """
    attempts = 2
    print('Type in the correct spelling out of these three options. You have 2 attempts\n')
    print(word, end = '\n\n')
    solution = phonemes[phoneme]['spelling'][word][0]
    options = list(phonemes[phoneme]['spelling'][word])
    random.shuffle(options)
    print(', '.join(options))
    while attempts > 0:
        answer = input(f'{attempts}. ').lower().strip()
        if answer == solution:
            print('Yes!\n')
            return
        elif not answer.isalpha() or answer not in options:
            print('Invalid entry')
            continue
        else:
            attempts -= 1
    print(f"Careful: the spelling of {word} is '{solution}'\n")


def homophones(phoneme):
    """Create a sample list of homophones to be tested.

    Args:
        phoneme (str): Phoneme being studied.
    """
    homoph_selection = list(phonemes[phoneme]['homophones'])
    if len(homoph_selection) > 5:
        homoph_selection = random.sample(homoph_selection, k = 5)
    else:
        random.shuffle(homoph_selection)
    print('\nEach of the following phoneme combinations has homophones. You have 5 attempts to find them all')
    for index, homoph in enumerate(homoph_selection):
        all_spellings = phonemes[phoneme]['homophones'][homoph].copy()
        print(f"\n{index+1}. {homoph} has {len(all_spellings)} homophones")
        find_homs(homoph, all_spellings)   

       
def find_homs(homoph, all_spellings):
    """Test knowledge of homophones.
    
    5 attempts to guess all the spellings of each homophone (amount shown by the app). If failed, the app shows the solutions.

    Args:
        homoph (str): Phonemic transcription to guess the spellings of.
        all_spellings (set): Set of all the homophones of 'homoph'.
    """
    attempts = 5
    full_len = len(all_spellings)
    while attempts > 0:
        answer = input(f'{attempts}. ').lower().strip()
        if not answer.isalpha():
            print('Only letters')
            continue
        elif answer in all_spellings:
            all_spellings.discard(answer)
            if len(all_spellings) == 0:
                print('All done!')
                return
            print(f'Yes! {len(all_spellings)} to go')
            attempts -= 1
        else:
            attempts -= 1
    if len(all_spellings) == full_len:
        print(f"All the homophones of {homoph} are {', '.join(all_spellings)}")
    else:
        print(f"The remaining homophones of {homoph} are {', '.join(all_spellings)}")
    
    
def save_progress(phoneme, seen, audio):
    """Save phoneme studied to a JSON file for future review and to avoid repetition.

    Args:
        phoneme (str): Phoneme being studied.
        seen (dict): Mapping of previously studied phonemes to their audio.
        audio (str | None):
            - Path to downloaded file if available.
            - 'offline' if there is no internet connection.
            - None if audio is unavailable or an error occurred.
    """

    seen[phoneme] = audio
    data = {'Phonemes seen' : seen}
    
    with open(file_path, 'w') as f:
        json.dump(data, f)
        logger.info(f'{phoneme} successfully saved/updated to {file_path}')

       
def load_progress():
    """Look for JSON file with previously covered phonemes.

    Returns:
        dict : Mapping of previously covered phonemes to their audio.
               Return an empty dictionary if the file doesn't exist. 
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
            logger.info(f'English_Pronunciation_Trainer.json successfully loaded from {file_path}')
            return data['Phonemes seen']
    except FileNotFoundError:
        logger.info('Empty dictionary created since English_Pronunciation_Trainer.json does not exist')
        return {}


def review(seen):
    """Trigger review of all previously covered phonemes through 'review_spell()' and 'review_homophones()'.

    Args:
        seen (dict): Mapping of previously covered phonemes to their audio.
    """
    print(f'\nPhonemes covered so far: {', '.join(seen)}\n')
    for phoneme in seen:
        audio = seen[phoneme]
        if not audio or (audio == 'offline' and not online()):
            print(f'-{phoneme} : audio unavailable')         
        elif audio == 'offline' and online():
            update_audio(phoneme, seen)
        else:
            print(f'-{phoneme}')
            playsound(seen[phoneme])
    print()        
    review_spell(seen)
    review_homophones(seen)
    print()
                
def update_audio(phoneme, seen):
    """Update the real status of the audio for each phoneme in the JSON file if an internet connection is accessed.

    Args:
        phoneme (str): Previously covered phoneme.
        seen (dict): Mapping of previously covered phonemes to their audio.
    """
    audio_sound = get_phoneme(phonemes[phoneme]['api'])
    if audio_sound:
        print(f'-{phoneme}')
        playsound(audio_sound)  
    else:
        print(f'-{phoneme} : audio unavailable')
    save_progress(phoneme, seen, audio_sound)
    
    
def review_spell(seen):
    """Review spelling of previously covered words based on their phonemic transcription.
    
    Create a dictionary with 2 words for each phoneme covered, which are then shuffled. Key = phonemic transcription, Value = [phoneme, correct spelling].
    'test_no_help()' and 'test_with_help()' are called just like when learning a new phoneme.

    Args:
        seen (dict): Mapping of previously covered phonemes to their audio.
    """
    matches = {}
    for phoneme in seen:
        guesses_list = list(phonemes[phoneme]['spelling'])
        two_guesses = random.sample(guesses_list, k = 2)

        for word in two_guesses:
            matches[word] = [phoneme, phonemes[phoneme]['spelling'][word][0]]
    words_to_guess = list(matches)
    random.shuffle(words_to_guess)
    retry_review = []

    for index, word in enumerate(words_to_guess):
        print(f'{index + 1}. How do you spell {word}? - You have 5 attempts')
        test_no_help(word, retry_review, matches[word][0] )
    
    if retry_review:
        for word in retry_review:
            test_with_help(word, matches[word][0])
            
            
def review_homophones(seen):
    """Review homophones of previously covered phonemes.
    
    Create a dictionary with 2 words for each phoneme, which are then shuffled. Key = word to spell, Value = phoneme.
    'find_homs()' is called just like with a new phoneme.

    Args:
        seen (dict): Mapping of previously covered phonemes to their audio.
    """
    homophones_pool = {}
    for phoneme in seen:
        hom_list = list(phonemes[phoneme]['homophones'])
        two_homs = random.sample(hom_list, k = 2)
        
        for hom in two_homs:
            homophones_pool[hom] = phoneme
    homophones_to_guess = list(homophones_pool)
    random.shuffle(homophones_to_guess)
    
    print('\nEach of the following phoneme combinations has homophones. You have 5 attempts to find them all')
    for index, homoph in enumerate(homophones_to_guess):
        all_spellings = phonemes[homophones_pool[homoph]]['homophones'][homoph].copy()
        print(f"\n{index+1}. {homoph} has {len(all_spellings)} homophones")
        find_homs(homoph, all_spellings)        
        
        
def activities(seen):
    """If 'seen' exists, the app asks if the user just wants to review previous phonemes or learn a new one as well.
    
    Review is mandatory and skipping it is purposely not given as an option.

    Args:
        seen (dict): Mapping of previously covered phonemes to their audio.

    Returns:
        list | None : 
            - List of remaining new unexplored phonemes to study.
            - None if only 'review' is selected or if there are no more new phonemes to learn.
    """
    phonemes_pool = [phoneme for phoneme in phonemes if phoneme not in seen]
    while True:
        if not phonemes_pool:
            print('There are no new phonemes to learn so we can only review previous ones')
            review(seen)
            print('End of review. See you soon!')
            logger.info('Review ended and ending program as there are no new phonemes to study')
            return None
        
        ask = input('Do you want to simply review old phonemes or learn a new one as well?  r = only review, l = review and learn: ').lower().strip()
        if ask == 'r':
            review(seen)
            print('End of review. See you soon!')
            logger.info('Ending program after review as requested by user')
            return None
        if ask == 'l':
            review(seen)
            print('End of review\n')
            if phonemes_pool:
                print("Now let's learn a new phoneme. Starting in 3 seconds.\n")
                time.sleep(3)
                logger.info('Review ended')
                return phonemes_pool
        else:
            print('Invalid input. Only r/l')
            
            
def main():
    """Runs the English Pronunciation Trainer.
    
    Checks for pre-existing JSON file and enforces review if it exists.
    Teaches one new phoneme per session through spelling and homophones exercises.
    Saves phoneme covered to a JSON file
    """
    
    logger.info('App successfully started')
    print('Welcome to the English Pronunciation Trainer!\n')
    if not online():
        print('We are offline so the audio can not be played\n')
    seen = load_progress()
    
    if not seen:
        phonemes_pool = list(phonemes)
        logger.info('No previous progress - starting from scratch')
    else:
        logger.info('Review started successfully')
        phonemes_pool = activities(seen)
        if not phonemes_pool:
            return
        
    print('LEARNING')
    phoneme = random.choice(list(phonemes_pool))
    logger.info(f'Starting learning process for phoneme {phoneme}')
    audio = learn(phoneme)
    
    logger.info('Starting practice')
    print('\nPRACTICE')
    spell(phoneme, audio)
    
    logger.info('Starting homophones')
    print('\nHOMOPHONES')
    homophones(phoneme = phoneme)
    
    print('\nGreat work and see you soon!')
    save_progress(phoneme, seen, audio)
    logger.info(f'Session for {phoneme} ended')


if __name__ == '__main__':
    main()