import random
from phoneme_api import get_phoneme
import json
from pathlib import Path
import log_file
import logging
from phonemes_dict import phonemes
from fastapi import HTTPException
from copy import deepcopy
from uuid import uuid4

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".english_pronunciation_trainer"

file_path = DATA_DIR / "progress.json"


ONGOING_TESTS = {}

def get_phonemes_pool():
    logger.info('App successfully started')
    seen = load_progress()
    if not seen:
        phonemes_pool = list(phonemes)
        logger.info('No previous progress - starting from scratch')
    else:
        logger.info('Review started successfully')
        phonemes_pool = [phoneme for phoneme in phonemes if phoneme not in seen]
    return phonemes_pool
    
        
def patterns():
    phoneme = random.choice(list(get_phonemes_pool()))
    patterns = {pattern: random.sample(example, k = 2) for pattern, example in phonemes[phoneme]['patterns'].items()}
    return phoneme, patterns


def phonemes_covered():
    seen = load_progress()
    seen_list = []
    
    for phoneme in seen:
        audio_file = get_phoneme(phonemes[phoneme]['api'])
        audio_url = f'/audio/{Path(audio_file).name}' if audio_file else None
        phon = {'phoneme': phoneme, 'audio_url': audio_url}
        seen_list.append(phon)
    return seen_list
    

def create_spell_tests(pairs):
    test_words = []

    for word, phoneme in pairs:
        solution = phonemes[phoneme]['spelling'][word][0]
        options = list(phonemes[phoneme]['spelling'][word])
        random.shuffle(options)
        test_id = f'spell_test_{uuid4().hex}'
        ONGOING_TESTS[test_id] = {'word': word, 
                                  'phoneme': phoneme, 
                                  'solution': solution, 
                                  'attempts_left': 5,
                                  'with_help': False}
        test_words.append({'word': word, 
                           'test_id': test_id, 
                           'options': options
                           })
    
    return test_words


def check_spell_answer(user_input):
    if user_input['test_id'] not in ONGOING_TESTS:
        raise HTTPException(status_code=404, detail='Word not found')
    test = ONGOING_TESTS[user_input['test_id']]  
    
    if user_input['answer'] == test['solution']:
        ONGOING_TESTS.pop(user_input['test_id'])
        return {'answered': 'correct'}
    
    if test['with_help'] and test['attempts_left'] != 1:
        test['attempts_left'] = 2
        
    test['attempts_left'] -=1
    
    if test['attempts_left'] < 1:
        if test['with_help']:
            ONGOING_TESTS.pop(user_input['test_id'])
            return {'answered': 'failed_all', 'solution': test['solution']} 
        
        test['with_help'] = True
        return {'answered': 'failed'}
    
    return {'answered': 'incorrect', 'attempts_left': test['attempts_left']}
    
      
def spell_learn(phoneme):
    words_list = random.sample(list(phonemes[phoneme]['spelling']), k = 5)
    pairs =  [(word, phoneme) for word in words_list]
    return create_spell_tests(pairs)


def create_homophones_test(pairs): 
    test_homophones = []
    
    for homoph, phoneme in pairs:
        all_spellings = phonemes[phoneme]['homophones'][homoph]
        length_solution = len(all_spellings)
        solutions_left = deepcopy(all_spellings)
        test_id = f'homoph_test_{uuid4().hex}'
        ONGOING_TESTS[test_id] = {'homoph': homoph, 
                                  'solution': all_spellings, 
                                  'solutions_left': solutions_left,
                                  'amount': length_solution,
                                  'to_guess': length_solution,
                                  'attempts_left': 5}
        test_homophones.append({'homoph': homoph, 
                                'test_id': test_id, 
                                'amount': length_solution})
    return test_homophones


def check_homophone_answer(user_input):    
    if user_input['test_id'] not in ONGOING_TESTS:
        raise HTTPException(status_code=404, detail= 'Homophone not found')
    
    test = ONGOING_TESTS[user_input['test_id']]
    answer = user_input['answer']
    
    if answer in test['solutions_left']:
        test['to_guess'] -= 1
        test['solutions_left'].discard(answer)
        
        if test['to_guess'] == 0:
            return {'answered': 'done'}
        
        return {'answered': 'correct', 'attempts_left': test['attempts_left']}

    if test['attempts_left'] > 1:
        test['attempts_left'] -= 1
        return {'answered': 'incorrect', 'attempts_left': test['attempts_left']}
    

    if test['to_guess'] == test['amount']:
        return {'answered': 'failed_all', 'solution': test['solution']}
    return {'answered': 'failed', 'solution': test['solutions_left']}
    
    
        
def homophones_learn(phoneme):
    homoph_list = list(phonemes[phoneme]['homophones'])
    if len(homoph_list) > 5:
        homoph_list = random.sample(homoph_list, k = 5)
    else:
        random.shuffle(homoph_list)
    
    pairs = [(homoph, phoneme) for homoph in homoph_list]
    
    return create_homophones_test(pairs)

    
def save_progress(progress, seen):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    audio_filename = Path(progress['audio_path']).name if progress['audio_path'] else None

    seen[progress['new_phoneme']] = audio_filename
    data = {'Phonemes seen' : seen}
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
            logger.info(f"{progress['new_phoneme']} successfully saved/updated to {file_path}")
            
        return {'status': 'ok'}
    except OSError:
        logger.exception("Failed to save progress")
        raise HTTPException(status_code=500, detail="Failed to save progress")

       
def load_progress():

    try:
        with open(file_path) as f:
            data = json.load(f)
            logger.info(f'English_Pronunciation_Trainer.json successfully loaded from {file_path}')
            return data['Phonemes seen']
    except FileNotFoundError:
        logger.info('Empty dictionary created since English_Pronunciation_Trainer.json does not exist')
        return {}
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        logger.exception("Progress file unreadable; starting fresh")
        return {}


def review_spell(seen):
    pairs = []
    for phoneme in seen:
        word_options = list(phonemes[phoneme]['spelling'])
        two_word_options = random.sample(word_options, k = 2)
        pairs.extend((word, phoneme) for word in two_word_options)
    random.shuffle(pairs)
    return create_spell_tests(pairs)
            

def review_homophones(seen):
    pairs = []
    for phoneme in seen:
        homoph_options = list(phonemes[phoneme]['homophones'])
        two_homoph_options = random.sample(homoph_options, k = 2)
        pairs.extend((homoph, phoneme) for homoph in two_homoph_options)
    random.shuffle(pairs) 
    return create_homophones_test(pairs)


