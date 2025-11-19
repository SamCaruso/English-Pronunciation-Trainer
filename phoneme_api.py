"""
Phoneme API 

This module provides the function 'get_phoneme()' that fetches the audio reproduction of the given phoneme, 
if available, from the Free Dictionary API.
'download_audio()' downloads the audio into the local directory to reduce API calls.

Dependencies:
    requests
    playsound : if 'pip install playsound' does not work, try 'pip install playsound==1.2.2'
"""

import requests
from requests.exceptions import RequestException
from json import JSONDecodeError
import logging
from pathlib import Path


logger = logging.getLogger(__name__)

AUDIO_DIR = Path(__file__).parent / 'audio_repr'
AUDIO_DIR.mkdir(exist_ok = True)


def log_error_return(msg, e):
    """Handle errors gracefully and return None.
    
    Since this is a small project where all anticipated exceptions are already handled and recorded and very easily traceable,
    logger.ERROR is intentionally used instead of logger.EXCEPTION as tracebacks are unnecessary. 
    

    Args:
        msg (str): Custom message for each exception.
        e (Exception): Exception caught.

    Returns:
        bool: None
    """
    logger.error(f'{e.__class__.__name__} {msg} -> {e}')
    return None


def get_uk_audio(data, phoneme):
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
                    logger.info(f'Successfully retrieved the audio for {phoneme} through API')
                    return uk_audio                         
                else:
                    logger.error(f'Unsupported audio format for {phoneme}: {audio} should be .mp3/.wav')
    return None


def download_audio(audio, phoneme):
    """Convert and download audio into the local directory.

    Args:
        audio (str): URL of British audio.
        phoneme (str): Phoneme being studied.

    Returns:
        str | None: 
            - Path to the audio file downloaded.
            - None if a requests error occurs.
    """
    local_audio_file = AUDIO_DIR / f"{phoneme.replace('/', '')}.mp3"
    
    try:
        get_audio_bytes = requests.get(audio, timeout = 5)
        get_audio_bytes.raise_for_status()
        with open(local_audio_file, 'wb') as f:
            f.write(get_audio_bytes.content)
        logger.info(f'Successful download of audio for {phoneme} in {AUDIO_DIR}')
        return str(local_audio_file)
    except RequestException as e:
        return log_error_return(f'Download error for {phoneme}', e)


def get_phoneme(phoneme):
    """Fetch sound of phoneme from the Free Dictionary API.
    
    Only British English pronunciation is accepted for this app, but the Free Dictionary doesn't always have it.
    If that is the case, all possible exceptions are handled and logged so they can return a graceful user-friendly message in the main module.
    All exceptions related to the 'requests' module are caught as 'RequestException' for simplicity for the user,
    but all technical details are in 'log_file.py'.
    Only a JSON file is expected to be returned, so everything else is handled as an exception.
    Since the maximum amount of calls to the API per run is only 2, requests.Session() is intentionally omitted as its overhead is not justified.
    if __name__ == '__main__' is intentionally omitted as this module is meant to be imported.

    Args:
        phoneme (str): phoneme being studied and passed through the main module.

    Returns:
        str: Path to the audio file in the local directory.
    """
    local_audio_file = AUDIO_DIR / f"{phoneme.replace('/', '')}.mp3"
    
    if local_audio_file.exists():
        logger.info(f'Playing cached audio file for {phoneme}')
        return str(local_audio_file)
    
    try:
        sound = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{phoneme}', timeout=5)
        sound.raise_for_status()
        data = sound.json()
        if not isinstance(data, list):
            raise ValueError('Unexpected json format returned')
        
        audio_online = get_uk_audio(data, phoneme)
        if not audio_online:
            raise ValueError('Audio not found/not British/wrong format')

        local_audio_file = download_audio(audio_online, phoneme)    
        return local_audio_file
    except (RequestException, ValueError) as e:
        return log_error_return(f'for {phoneme}', e)
    except JSONDecodeError as e:
        return log_error_return(f'for {phoneme} -> Wrong file format: NOT JSON', e)