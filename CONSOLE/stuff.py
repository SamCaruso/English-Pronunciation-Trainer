def go(a):
    
    if a == 3:
        print(3)
    elif a > 3:
        print('greater')
        less(a)
    else:
        print('less')

def less(a):
    return a -30 
        
go(5)
import requests
from requests.exceptions import RequestException
from json import JSONDecodeError
import logging
from pathlib import Path
from playsound import playsound


#data = {{'word': 'air', 'phonetic': '/ˈɛə/', 'phonetics': [{'text': '/ˈɛə/', 'audio': 'https://api.dictionaryapi.dev/media/pronunciations/en/air-uk.mp3', 'sourceUrl': 'https://commons.wikimedia.org/w/index.php?curid=9014243', 'license': {'name': 'BY 3.0 US', 'url': 'https://creativecommons.org/licenses/by/3.0/us'}}, {'text': '/ˈɛəɹ/', 'audio': 'https://api.dictionaryapi.dev/media/pronunciations/en/air-us.mp3', 'sourceUrl': 'https://commons.wikimedia.org/w/index.php?curid=709463', 'license': {'name': 'BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0'}}], 'meanings': [{'partOfSpeech': 'noun', 'definitions': [{'definition': "The substance constituting earth's atmosphere, particularly:", 'synonyms': [], 'antonyms': [], 'example': "I'm going outside to get some air."}, {'definition': '(usually with the) The apparently open space above the ground which this substance fills, formerly thought to be limited by the firmament but now considered to be surrounded by the near vacuum of outer space.', 'synonyms': [], 'antonyms': [], 'example': 'The flock of birds took to the air.'}, {'definition': 'A breeze; a gentle wind.', 'synonyms': [], 'antonyms': []}, {'definition': 'A feeling or sense.', 'synonyms': [], 'antonyms': [], 'example': 'to give it an air of artistry and sophistication'}, {'definition': 'A sense of poise, graciousness, or quality.', 'synonyms': [], 'antonyms': []}, {'definition': '(usually in the plural) Pretension; snobbishness; pretence that one is better than others.', 'synonyms': [], 'antonyms': [], 'example': 'putting on airs'}, {'definition': 'A song, especially a solo; an aria.', 'synonyms': [], 'antonyms': []}, {'definition': 'Nothing; absence of anything.', 'synonyms': [], 'antonyms': []}, {'definition': 'An air conditioner or the processed air it produces.', 'synonyms': [], 'antonyms': [], 'example': 'Could you turn on the air?'}, {'definition': 'Any specific gas.', 'synonyms': [], 'antonyms': []}, {'definition': '(motor sports) A jump in which one becomes airborne.', 'synonyms': [], 'antonyms': []}, {'definition': 'A television or radio signal.', 'synonyms': [], 'antonyms': []}, {'definition': 'Publicity.', 'synonyms': [], 'antonyms': []}], 'synonyms': ['atmosphere', 'aura', 'gas', 'lift', 'nimbus'], 'antonyms': []}, {'partOfSpeech': 'verb', 'definitions': [{'definition': 'To bring (something) into contact with the air, so as to freshen or dry it.', 'synonyms': [], 'antonyms': []}, {'definition': 'To let fresh air into a room or a building, to ventilate.', 'synonyms': [], 'antonyms': []}, {'definition': 'To discuss varying viewpoints on a given topic.', 'synonyms': [], 'antonyms': []}, {'definition': 'To broadcast (a television show etc.).', 'synonyms': [], 'antonyms': []}, {'definition': 'To be broadcast.', 'synonyms': [], 'antonyms': [], 'example': 'This game show first aired in the 1990s and is still going today.'}, {'definition': 'To ignore.', 'synonyms': [], 'antonyms': []}], 'synonyms': [], 'antonyms': []}], 'license': {'name': 'CC BY-SA 3.0', 'url': 'https://creativecommons.org/licenses/by-sa/3.0'}, 'sourceUrls': ['https://en.wiktionary.org/wiki/air']}}


def get_uk_audio(data):
    """Parse API JSON and return British English audio (.mp3 or .wav) if available. 

    Args:
        data (list): Expected JSON format returned by the API.
        phoneme (str): Phoneme being studied.

    Returns:
        str | None:
            - URL of British audio.
            - None if British audio doesn't exist or if it is not .mp3/.wav.
    """
    for entry in data:
        for phonetics_block in entry.get('phonetics', []):
            audio = phonetics_block.get('audio', '')
            if "-uk" in audio:
                if audio.endswith(('.mp3', '.wav')):
                    uk_audio = audio
                    return uk_audio                         
    return None

#print(get_uk_audio(data))

a = {'a' :5, 'b' : 10, 'c':15,'d': 20, 'e':25}

b = a.keys()
print(b)

a['t'] = 30
print(b)
