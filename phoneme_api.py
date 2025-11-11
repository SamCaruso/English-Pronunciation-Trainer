"""
Phoneme API 

This module provides the function 'get_phoneme()' that fetches the audio reproduction of the given phoneme, 
if available, from the Free Dictionary API

Dependencies:
    requests
    playsound : if 'pip install playsound' does not work, try 'pip intall playsound==1.2.2'
"""

import requests
from playsound import playsound, PlaysoundException
from requests.exceptions import RequestException
from json import JSONDecodeError
import logging

logger = logging.getLogger(__name__)


def log_error_return(msg, e):
    """Handle errors gracefully and return False.
    
    Since this is a small project where all anticipated exceptions are already handled and recorded and very easily traceable,
    logger.ERROR is intentionally used instead of logger.EXCEPTION as tracebacks are unnecessary. 
    

    Args:
        msg (str): custom message for each exception
        e (Exception): exception caught

    Returns:
        bool: always returns False
    """
    logger.error(f'{e.__class__.__name__} {msg} -> {e}')
    return False


def get_phoneme(phoneme):
    """Retrieve and produce sound of phoneme from the Free Dictionary API.
    
    Only British English pronunciation is accepted for this app, but the Free Dictionary doesn't always have it.
    If that is the case, all possible exceptions are handled and logged so they can return a graceful user-friendly message in the main module.
    Only a json file is expected to be returned, so everything else is handled as an exception.
    Since the maximum amount of calls to the API per run is only 2, requests.Session() is intentionally omitted as its overhead is not justified.
    if __name__ == '__main__' is intentionally omitted as this module is meant to be imported.

    Args:
        phoneme (str): phoneme being studied and passed through the main module

    Raises:
        ValueError: British Pronunciation is not available

    Returns:
        bool: True if audio is available, False if not
    """

    try:
        sound = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{phoneme}', timeout=5)
        sound.raise_for_status()
        data = sound.json()
        aud = data[0]['phonetics'][0]['audio']
        if not aud:
            raise ValueError('Audio not found/provided. Some sounds only provide an American pronunciation but we want a British one')
        playsound(aud)
        logger.info(f'Successful retrieval of the audio for {phoneme} through API')
        return True
    except (RequestException, ValueError) as e:
        return log_error_return(f'for {phoneme}', e)
    except JSONDecodeError as e:
        return log_error_return(f'for {phoneme} -> Wrong file format: NOT JSON', e)
    except PlaysoundException as e:
        return log_error_return(f'for {phoneme} -> Invalid file format', e)
    except IndexError as e:
        return log_error_return(f'for {phoneme} -> File may have returned a different format from the one expected', e)