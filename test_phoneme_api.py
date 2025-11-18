""" 
Testing module for phoneme_api.py

The first Test Class mocks and tests the API in 'get_phoneme()'.
The second one tests the behaviour of 'log_error_return()'

"""


import unittest
from unittest.mock import patch, Mock
from phoneme_api import get_phoneme, log_error_return, get_uk_audio, download_audio
import logging
from json import JSONDecodeError
from requests.exceptions import HTTPError, ConnectionError, RequestException
from pathlib import Path
import tempfile

logging.getLogger('phoneme_api').disabled = True


class TestGetPhoneme(unittest.TestCase):
    """Test retrieval of the API in 'get_phoneme()' and exception handling"""

    def setUp(self):
        self.mock_response = Mock()
        self.mock_response.raise_for_status.return_value = None
        self.tempdir = tempfile.TemporaryDirectory()
        patcher = patch('phoneme_api.AUDIO_DIR', Path(self.tempdir.name))
        self.addCleanup(patcher.stop)
        self.mock_audio_dir = patcher.start()
        
        
    def tearDown(self):
        self.tempdir.cleanup()
        
    
    @patch('phoneme_api.get_uk_audio', return_value = None)
    @patch('phoneme_api.requests.get')
    def test_get_phoneme_successful_no_audio(self, mock_get, mock_uk_audio):           
        self.mock_response.json.return_value = [{'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': ''}]}]
        
        mock_get.return_value = self.mock_response
        result = get_phoneme('empty_phoneme')
        
        self.assertIsNone(result)
        self.mock_response.raise_for_status.assert_called_once()   
        mock_uk_audio.assert_called_once()
    
              
    @patch('phoneme_api.requests.get')
    def test_get_phoneme_successful_with_audio(self, mock_get):
        mock_get_phoneme = Mock()   
        mock_get_phoneme.raise_for_status.return_value = None
        mock_get_phoneme.json.return_value = [{'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': 'https://getaudio.url/good_phoneme-uk.mp3'}]}]
        
        mock_download_audio = Mock()
        mock_download_audio.raise_for_status.return_value = None
        mock_download_audio.content = b'good_phoneme_audio_bytes'
        
        mock_get.side_effect = [mock_get_phoneme, mock_download_audio]
        
        result = get_phoneme('good_phoneme')
        expected_file = Path(self.tempdir.name) / "good_phoneme.mp3"
        
        self.assertEqual(result, str(expected_file))
        mock_get_phoneme.raise_for_status.assert_called_once()
        mock_download_audio.raise_for_status.assert_called_once()
        mock_get.assert_any_call('https://api.dictionaryapi.dev/api/v2/entries/en/good_phoneme', timeout = 5)
        mock_get.assert_any_call('https://getaudio.url/good_phoneme-uk.mp3', timeout = 5)
        self.assertEqual(mock_get.call_count, 2)


    @patch('phoneme_api.requests.get')
    def test_api_not_called_audio_already_exists(self, mock_get):
        tempdir = tempfile.TemporaryDirectory()
        patcher = patch('phoneme_api.AUDIO_DIR', Path(tempdir.name))
        patcher.start()

        cached_file = Path(tempdir.name) / "phoneme.mp3"
        cached_file.write_bytes(b'test')

        result = get_phoneme('phoneme')

        self.assertEqual(result, str(cached_file))
        mock_get.assert_not_called()

        patcher.stop()


    @patch('phoneme_api.requests.get', side_effect = JSONDecodeError('Value expected', '', 0))
    def test_invalid_json(self, mock_get):
        result = get_phoneme('phoneme')
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/phoneme', timeout = 5)
        self.assertIsNone(result)
        
    
    @patch('phoneme_api.requests.get')
    def test_valid_json_invalid_expected_format(self, mock_get):
        self.mock_response.json.return_value = ({'phonetics': [{'text': '/ɔː(ɹ)/', 'audio': 'https://getaudio.url/phoneme.mp3'}]})
        
        mock_get.return_value = self.mock_response
        result = get_phoneme('phoneme')
        
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/phoneme', timeout = 5)
        self.assertIsNone(result)
        
    
    @patch('phoneme_api.requests.get', side_effect = HTTPError)
    def test_http_error(self, mock_get):   
        result = get_phoneme('non-existent-phoneme')
        
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/non-existent-phoneme', timeout = 5)
        self.assertIsNone(result)
        
    
    @patch('phoneme_api.requests.get', side_effect = ConnectionError)
    def test_connection_error(self, mock_get):
        result = get_phoneme('phoneme')
        mock_get.assert_called_once_with('https://api.dictionaryapi.dev/api/v2/entries/en/phoneme', timeout = 5)
        self.assertIsNone(result)
        
        

class TestGetUkAudio(unittest.TestCase):
    """Test return value of 'get_uk_audio()'"""
    
    def test_get_uk_audio_cases(self):
        
        cases = [
            ([{'phonetics': [{'audio': 'https://audio.url/phon-uk.mp3'}]}], 'https://audio.url/phon-uk.mp3'),
            ([{'phonetics': [{'audio': ''}]}], None), 
            ([{'phonetics': [{'audio': 'https://audio.url/phon-us.mp3'}]}], None),
            ([{'phonetics': [{'audio': 'https://audio.url/phon-uk.mp4'}]}], None),
            ([{'phonetics': [{'audio': 'https://audio.url/phon-uk.wav'}]}], 'https://audio.url/phon-uk.wav'),
            ([{'phonetics': [{'audio': ()}]}], None),
            ([{'phonetics': [{'audio': 'https://audio.url/phon-us.mp3'}, {'audio': 'https://audio.url/phon-uk.mp3'}]}], 'https://audio.url/phon-uk.mp3')
        ]
        
        for data, result in cases:
            with self.subTest(data = data, result = result):
                uk_audio = get_uk_audio(data, 'phon')
                self.assertEqual(uk_audio, result)



class TestDownloadAudio(unittest.TestCase):
    """Test return value of 'download_audio()'"""
    
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        patcher = patch('phoneme_api.AUDIO_DIR', Path(self.tempdir.name))
        self.addCleanup(patcher.stop)
        self.mock_audio_dir = patcher.start()
        self.audio = 'https://api.dictionaryapi.dev/media/pronunciations/en/phoneme-uk.mp3'
        
    def tearDown(self):
        self.tempdir.cleanup()
        
              
    @patch('phoneme_api.requests.get')
    def test_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'audio bytes'    
        
        mock_get.return_value = mock_response
        expected_result = str(Path(self.tempdir.name)/'phoneme.mp3')
        result = download_audio(self.audio, 'phoneme')
        
        self.assertEqual(result, expected_result)
        self.assertTrue(Path(expected_result).exists())
        mock_get.assert_called_once_with(self.audio, timeout = 5)
        mock_response.raise_for_status.assert_called_once()
        
        
    @patch('phoneme_api.requests.get', side_effect = RequestException)
    def test_fail(self, mock_get):
        result = download_audio(self.audio, 'phoneme')
        
        self.assertIsNone(result)
        
        
class TestLogger(unittest.TestCase):
    """Tests behaviour of 'log_error_return()'"""
    
    def test_logger_valid(self):
        self.assertFalse(log_error_return('msg', 'ex'))
    
    
    def test_logger_invalid_one_arg(self):
        with self.assertRaises(TypeError):
            log_error_return('one argument')
                

            
if __name__ == '__main__':
    unittest.main()