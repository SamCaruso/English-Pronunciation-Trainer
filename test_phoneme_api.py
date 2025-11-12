""" 
Testing module for Phoneme_api.py

The first Test Class mocks and tests the API in 'get_phoneme()'.
The second one tests the behaviour of 'log_error_return()'

"""


import unittest
from unittest.mock import patch, Mock
from phoneme_api import get_phoneme, log_error_return
import logging
from json import JSONDecodeError
from requests.exceptions import HTTPError, ConnectionError
from playsound import PlaysoundException

logging.getLogger('phoneme_api').disabled = True


class TestPhonemeApi(unittest.TestCase):
    """Test retrieval of the API in 'get_phoneme()' and exception handling"""
    
    @patch('phoneme_api.requests.get')
    def test_get_phoneme_successful_no_audio(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': ''}]}]
        
        mock_get.return_value = mock_response
        result = get_phoneme('empty_phoneme')
        
        self.assertFalse(result)
        
    
    @patch('phoneme_api.playsound')
    @patch('phoneme_api.requests.get')
    def test_get_phoneme_successful_with_audio(self, mock_get, mock_playsound):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': 'https://soundaudio.url/good_phoneme.mp3'}]}]
        
        mock_get.return_value = mock_response        
        result = get_phoneme('good_phoneme')
        
        self.assertTrue(result)
        mock_response.raise_for_status.assert_called_once()
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/good_phoneme', timeout = 5)
        
        mock_playsound.assert_called_once_with('https://soundaudio.url/good_phoneme.mp3')
        
    
    @patch('phoneme_api.playsound', side_effect = PlaysoundException)
    @patch('phoneme_api.requests.get')
    def test_invalid_audio_input(self, mock_get, mock_playsound):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': 'https://soundaudio.url/phoneme.mp4'}]}]
        
        mock_get.return_value = mock_response
        
        result = get_phoneme('phoneme')
        self.assertFalse(result)
        
    
    @patch('phoneme_api.requests.get', side_effect = JSONDecodeError('Value expected', '', 0))
    def test_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        
        mock_get.return_value = mock_response
        result = get_phoneme('phoneme')
        
        self.assertFalse(result)
       
      
    @patch('phoneme_api.requests.get')
    def test_valid_json_unexpected_format_indexerror(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {'phonetics': {'text': '/ɔː(ɹ)/', 'audio': 'https://soundaudio.url/good_phoneme.mp3'}}
        
        mock_get.return_value = mock_response
        result = get_phoneme('phoneme')
        
        self.assertFalse(result)
        
    
    @patch('phoneme_api.requests.get', side_effect = HTTPError)
    def test_HTTPError_non_existent_phoneme(self, mock_get):
        mock_response = Mock()
        
        mock_get.return_value = mock_response
        result = get_phoneme('non_existent_phoneme')
        
        self.assertFalse(result)
        
    
    @patch('phoneme_api.requests.get', side_effect = ConnectionError)
    def test_connection_error(self, mock_get):
        result = get_phoneme('phoneme')
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/phoneme', timeout = 5)
        self.assertFalse(result)
        
        
class TestLogger(unittest.TestCase):
    """Tests behaviour of 'log_error_return()'"""
    
    def test_logger_valid(self):
        self.assertFalse(log_error_return('msg', 'ex'))
    
    
    def test_logger_invalid_one_arg(self):
        with self.assertRaises(TypeError):
            log_error_return('one argument')
                

            
if __name__ == '__main__':
    unittest.main() 