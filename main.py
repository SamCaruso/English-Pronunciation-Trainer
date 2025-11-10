"""
English Pronunciation Trainer

This console-based app helps the user understand and memorise the most common spelling-pronunciation patterns of English phonemes(=sounds).

Overview:
1.Requires previous technical knowledge of pronunciation and it is based on Standard BRITISH ENGLISH.
2.Requires an Internet connection to access sounds through the Free Dictionary API.
3.Introduces one new sound at a time and shows its most common spelling patterns with examples.
4.Offers randomised spelling exercises.
5.Drills homophones

Features:
1.Progress is saved to a JSON file used for reviewing previously studied sounds.
2.Only 1 new sound can be studied per session to promote gradual learning.
3.For the same reason, review at the beginning of every session (after the first one) is enforced and not optional.
3.The dictionary 'phonemes' and all its content is manually created by me to ensure accuracy.
4.If the Free Dictionary API doesn't provide the BRITISH ENGLISH version of the sounds, I handle it gracefully by showing that the pronunciation is not available.

Modules:
1. main : core exercises and review. Since the code for review relies heavily on functions defined in the main script, I decided to leave it there instead of moving it to a separate module.
2. pronunciaition_api : handling of the Free Dictionary API to reproduce the sound of phonemes if available """

import random
from phoneme_api import get_phoneme
import json
import time
import os

file_path = os.path.join(os.path.dirname(__file__), 'English_Pronunciation_Trainer.json')

phonemes = {'/ɔ:/' : 
    {'patterns' : 
        {'aw' : ('saw', 'yawn', 'draw'), 'ore' : ('core', 'snore', 'before'), 'oar' : ('board', 'coarse', 'soar'), 'or' : ('port', 'absorb', 'corn'), 'au' : ('august', 'autumn', 'flaunt'), 'oor' : ('door', 'floor', 'poor'), 'our' : ('mourn', 'pour', 'four'), 'war' : ('war', 'award', 'swarm')},
        'spelling' : {"/'ɔ:də/" : ('order', 'aurder', 'awder'), "/'kɔ:ʃən/" : ('caution', 'courtion', 'coretion'), "/wɔ:d/" : ('ward', 'word', 'woard'), "/lɔ:ntʃ/" : ('launch', 'lunch', 'lawnch'), "/dɔ:n/" : ('dawn', 'down', 'daun'), "/dʒɔ:/" : ('jaw', 'jore', 'joor'), "/dɪ'vɔ:s/" : ('divorce', 'divauce', 'divawrce'), "/ə'fɔ:d/" : ('afford', 'affawd', 'affaud'), '/stɔ:/' : ('store', 'stoar', 'stour'), "/swɔ:/" : ('swore', 'swar', 'swor')}, 
        'homophones' : {'/ɔ:/' : {'or', 'oar', 'awe', 'ore'},  '/sɔ:/' : {'saw', 'sore', 'soar'}, '/bɔ:d/' : {'bored', 'board'}, '/flɔ:/' : {'floor', 'flaw'}, '/ʃɔ:/' : {'shore', 'sure'}, '/pɔ:/' : {'poor', 'paw', 'pore', 'pour'}, '/sɔ:s/' : {'sauce', 'source'}, "/'mɔ:nɪŋ/" : {'morning', 'mourning'}, '/stɔ:k/' : {'stalk', 'stork'}, '/wɔ:/' : {'war', 'wore'}}},
    '/ɜ:/' : 
        {'patterns' : 
            {'er + con' : ('alert', 'deserve', 'universe'), 'ir + con' : ('girl', 'third', 'dirt'), 'wor + con' : ('word', 'work', 'worse'), 'ur + con' : ('curl', 'burden', 'lurk'), 'ear + con' : ('pearl', 'hearse', 'learn')}, 
            'spelling' : {'/wɜ:m/' : ('worm', 'warm', 'werm'), '/ʃɜ:t/' : ('shirt', 'shert', 'short'), '/bɜ:st/' : ('burst', 'birst', 'berst'), '/pɜ:k/' : ('perk', 'purk', 'pirk'), '/fɜ:m/' : ('firm', 'furm', 'ferm')}, 
            'homophones' : {'/hɜ:d/' : {'heard', 'herd'}, '/fɜ:/' : {'fir', 'fur'}, '/wɜ:d/' : {'word', 'whirred'}, '/kɜ:b/' : {'kerb', 'curb'}}},
        '/eə/' : {
            'patterns' : {
                'are' : ('care', 'stare', 'ware'), 'air' : ('affair', 'chair', 'repair'), 'ear' : ('swear', 'pear', 'bear')},
            'spelling' : {'/leə/' : ('lair', 'lare', 'lere'), '/preə/' : ('prayer', 'prare', 'prair'), "/ˌvedʒə'teəriən/" : ('vegetarian', 'vegetearian', 'vegetairian'), "/'peərənt/" : ('parent', 'pairent', 'perent'), "/'veəri/" : ('vary', 'very', 'veary')},
            'homophones' : {'/feə/' : {'fair', 'fare'}, '/peə/' : {'pare', 'pair', 'pear'}, '/heə/' : {'hair', 'hare'}, '/steə/' : {'stare', 'stair'}, '/fleə/' : {'flair', 'flare'}}
            }}


def learn(phoneme):
    print(f'New phoneme = {phoneme}\n')
    pron = get_phoneme(phoneme)
    if not pron:
        print('Pronunciation unavailable')
    print('The most common spelling patterns for this phoneme are: \n')

    for pattern, example in phonemes[phoneme]['patterns'].items():
        examples = ', '.join(random.sample(example, k = 2))
        print(f'{pattern.upper()} -> {examples}')
    return pron
        

def spell(phoneme, pron):
    if not pron:
        print('Write the word that corresponds to the following phonemes. You have 5 attempts')
    else:
        while True:
            ask = input('Write the word that corresponds to the following phonemes. You have 5 attempts. Do you want to listen to the target phoneme one more time? (y/n): ').lower().strip()
            if ask == 'y':
                get_phoneme(phoneme)
                break
            elif ask == 'n':
                break
            else:
                print('Invalid entry. Only y/n')
            
    words = random.sample(list(phonemes[phoneme]['spelling']), k = 5)
    retry = []
    spell_tests(words, retry, phoneme)

    
def spell_tests(words_list, retry_list, phoneme):
    
    for index, word in enumerate(words_list):
        print(f'{index + 1}. How do you spell {word}?')
        test_no_help(word, retry_list, phoneme)
    
    if retry_list:
        for word in retry_list:
            test_with_help(word, phoneme)
                
    
def test_no_help(word, retry, phoneme):
    attempts = 5
    while attempts > 0:
        answer = input(f'{attempts}. ').lower().strip()
        solution = phonemes[phoneme]['spelling'][word][0]
        if answer == solution:
            print('Yes\n')
            return
        if not answer.isalpha():
            print('Only letters')
            continue
        else:
            attempts -= 1
    retry.append(word)
    print()
  
    
def test_with_help(word, phoneme):
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
    phoneme_combos = list(phonemes[phoneme]['homophones'])
    if len(phoneme_combos) > 5:
        phoneme_combos = random.sample(phoneme_combos, k = 5)
    else:
        random.shuffle(phoneme_combos)
    print('\nEach of the following phoneme combinations has homophones. You have 5 attempts to find them all')
    for index, combo in enumerate(phoneme_combos):
        list_hom = phonemes[phoneme]['homophones'][combo].copy()
        print(f"\n{index+1}. {combo} has {len(list_hom)} homophones")
        find_homs(combo, list_hom)   

       
def find_homs(combo, list_hom):
    attempts = 5
    full_len = len(list_hom)
    while attempts > 0:
        answer = input(f'{attempts}. ').lower().strip()
        if not answer.isalpha():
            print('Only letters')
            continue
        elif answer in list_hom:
            list_hom.discard(answer)
            if len(list_hom) == 0:
                print('All done!')
                return
            print(f'Yes! {len(list_hom)} to go')
            attempts -= 1
        else:
            attempts -= 1
    if len(list_hom) == full_len:
        print(f"All the homophones of {combo} are {', '.join(list_hom)}")
    else:
        print(f"The remaining homophones of {combo} are {', '.join(list_hom)}")
    
    
def save_progress(phoneme, seen):
    if phoneme not in seen:
        seen.append(phoneme)
    data = {'Phonemes seen' : seen}
    
    with open(file_path, 'w') as f:
        json.dump(data, f)

       
def load_progress():
    try:
        with open(file_path) as f:
            data = json.load(f)
            return data['Phonemes seen']
    except FileNotFoundError:
        return []


def review(seen):
    print(f'\nPhonemes covered so far: {', '.join(seen)}\n')
    
    review_spell(seen)
    review_homophones(seen)
    print()
    
    
def review_spell(seen):
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
    homophones_pool = {}
    for phoneme in seen:
        hom_list = list(phonemes[phoneme]['homophones'])
        two_homs = random.sample(hom_list, k = 2)
        
        for hom in two_homs:
            homophones_pool[hom] = phoneme
    homophones_to_guess = list(homophones_pool)
    random.shuffle(homophones_to_guess)
    
    print('\nEach of the following phoneme combinations has homophones. You have 5 attempts to find them all')
    for index, combo in enumerate(homophones_to_guess):
        list_hom = phonemes[homophones_pool[combo]]['homophones'][combo].copy()
        print(f"\n{index+1}. {combo} has {len(list_hom)} homophones")
        find_homs(combo, list_hom)        
        
        
def activities(seen):
    phonemes_pool = [phoneme for phoneme in phonemes if phoneme not in seen]
    while True:
        ask = input('Do you want to simply review old phonemes or learn a new one as well?  r = only review, l = review and learn: ').lower().strip()
        if ask == 'r':
            review(seen)
            print('End of review')
            return None
        if ask == 'l':
            review(seen)
            print('End of review\n')
            if phonemes_pool:
                print("Now let's learn a new phoneme. Starting in 3 seconds.\n")
                time.sleep(3)
                return phonemes_pool
            else:
                print('No new phonemes to learn')
                return None
        else:
            print('Invalid input. Only r/l')
            
            
def main():
    print('Welcome to the English Pronunciation Trainer!\n')
    seen = load_progress()
    
    if not seen:
        phonemes_pool = list(phonemes)
    else:
        phonemes_pool = activities(seen)
        if not phonemes_pool:
            return
        
    print('LEARNING')
    phoneme = random.choice(list(phonemes_pool))
    pron = learn(phoneme)
    print('\nPRACTICE')
    spell(phoneme, pron)
    print('\nHOMOPHONES')
    homophones(phoneme = phoneme)
    save_progress(phoneme, seen)


if __name__ == '__main__':
    main()