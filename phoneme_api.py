import requests
from playsound import playsound, PlaysoundException
from requests.exceptions import RequestException


def get_phoneme(phoneme):
    phonemes = {'/ɔ:/' : 'or', '/ɜ:/' : 'err', '/eə/' : 'air'}
    choice = phonemes[phoneme]

    try:
        sound = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{choice}', timeout=5)
        sound.raise_for_status()
        data = sound.json()
        aud = data[0]['phonetics'][0]['audio']
        if not aud:
            raise ValueError
        playsound(aud)
        return True
    except (RequestException, ValueError, PlaysoundException, IndexError):
        return False