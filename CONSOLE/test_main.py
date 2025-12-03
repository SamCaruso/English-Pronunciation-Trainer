"""
Testing module for main.py through unittest.

Since this is a simple input-cased console app, I mock json file handling and a couple of user-input functions, 
but I intentionally omit further testing as it would be trivial and repetitive for this type of app.

"""


import unittest
from unittest.mock import patch, Mock, mock_open
import json
import main
from io import StringIO
from pathlib import Path
from requests.exceptions import RequestException
import logging

logging.getLogger('main').disabled = True


class BaseTest(unittest.TestCase):
    """Base class for reusable test helper"""
    
    def help_patch(self, func, func_args, user_input, expected, not_expected = None):
        """Helper function that patches input and checks result, to avoid boilerplate code in every test.

        Args:
            func (callable): Function needed.
            func_args (tuple): Arguments to pass into the function.
            user_input (list): Simulation of user input.
            expected (str): Expected response from the function.
            not_expected (str, optional): Response the function shouldn't return. Defaults to None.

        Returns:
            str: Captured output of 'test_with_help()'
        """
        
        with patch('builtins.input', side_effect = user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                func(*func_args)
                output = fake.getvalue()  
                
                if isinstance(expected, str):
                    expected = [expected]
                for sentence in expected:
                    self.assertIn(sentence, output)
                
                if not_expected:        
                    if isinstance(not_expected, str):
                        not_expected = [not_expected]
                    for sentence in not_expected:
                        self.assertNotIn(sentence, output)
        return output
    


class TestJson(unittest.TestCase):
    """Test creation, saving and loading of a json file for progress"""
    
    def test_load_progress_with_file(self):
        path = '/path/air.mp3'
        mock_data = json.dumps({'Phonemes seen' : {'/eə/': path}})
        
        with patch('builtins.open', mock_open(read_data = mock_data)):
            seen = main.load_progress()
            
        self.assertEqual(seen, {'/eə/': path})
        
    
    def test_load_progress_no_file(self):
        with patch('builtins.open', side_effect = FileNotFoundError):
            seen = main.load_progress()
            
        self.assertEqual(seen, {})
        
    
    def test_save_progress(self):
        path = {'/ɔ:/': '/path/or.mp3', '/eə/': 'path/air.mp3', '/ɜ:/': None, '/i:/': 'path/e.mp3'}
        
        cases = [
            ('/ɔ:/', {'/ɔ:/': path['/ɔ:/'], '/ɜ:/': None}, {'Phonemes seen': {'/ɔ:/': path['/ɔ:/'], '/ɜ:/': None}}),
            ('/i:/', {}, {'Phonemes seen': {'/i:/': path['/i:/']}}),
            ('/eə/', {'/i:/': path['/i:/'], '/ɜ:/': None}, {'Phonemes seen': {'/i:/': path['/i:/'], '/ɜ:/': None, '/eə/': path['/eə/']}})
        ]
        
        for phoneme, initial_seen, final_seen in cases:
            with self.subTest(phoneme = phoneme, initial_seen = initial_seen, final_seen = final_seen):
                m = mock_open()
                with patch('builtins.open', m):
                    main.save_progress(phoneme, initial_seen, path[phoneme])
                    
                    written = "".join(call.args[0] for call in m().write.call_args_list)
                    self.assertEqual(json.loads(written), final_seen)
                    
                    

class TestOnline(unittest.TestCase):
    """Test check for internet connection"""
    
    @patch('main.requests.head')
    def test_internet_accessed(self, mock_head):
        result = main.online()
        
        self.assertTrue(result)
        
    
    @patch('main.requests.head', side_effect = RequestException)
    def test_no_internet(self, mock_head):
        result = main.online()
        
        self.assertFalse(result)
        
        
        
class TestLearn(unittest.TestCase):
    """Test behaviour of 'learn()'"""
    @patch('main.online', return_value = True)
    @patch('main.playsound')
    @patch('main.get_phoneme')
    def test_learn_online(self, mock_get, mock_playsound, mock_online):
        
        cases = [('/ɔ:/', 'path/or.mp3'), ('/ɜ:/', None)]
        
        for phoneme, path in cases:
            with self.subTest(phoneme = phoneme, path = path):
                mock_get.return_value = path
            
                with patch('sys.stdout', new_callable=StringIO):
                    audio = main.learn(phoneme)
                
                if audio:
                    mock_playsound.assert_called_once_with(audio)
                else:
                    mock_playsound.assert_not_called()
                
                self.assertEqual(audio, path)
                mock_get.assert_called_once_with(main.phonemes[phoneme]['api'])
                    
                mock_get.reset_mock()
                mock_playsound.reset_mock()
                
                
    @patch('main.online', return_value = False)            
    @patch('main.get_phoneme')
    def test_learn_offline(self, mock_get, mock_online):
        phonemes = ['/i:/', '/ɜ:/']
        
        for phoneme in phonemes:
            with self.subTest(phoneme = phoneme):
                with patch('sys.stdout', new_callable=StringIO):
                    audio = main.learn(phoneme)
                
                self.assertEqual(audio, 'offline')
                mock_get.assert_not_called()
                
                mock_get.reset_mock()
                
                
                
class TestWithHelp(BaseTest):
    """Test behaviour of 'test_with_help()' based on user input.
    
    subTest is intentionally omitted to promote readability: grouping all these cases together under a single subTest 
    would create too many variables to unpack"""
    
    def test_correct_first_attempt(self):
        word = '/leə/'
        phoneme = '/eə/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = [correct_spell]
        
        self.help_patch(main.test_with_help, (word, phoneme), user_input, 'Yes!', 'Invalid entry')
    
                    
    def test_fail_then_correct(self):
        word = '/wɜ:m/'
        phoneme = '/ɜ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['warm', correct_spell]
        
        self.help_patch(main.test_with_help, (word, phoneme), user_input, 'Yes!', 'Invalid entry')

        
    def test_fail_both_valid_entries(self):
        word = "/'ɔ:də/"
        phoneme = '/ɔ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['awder', 'aurder']
        
        self.help_patch(main.test_with_help, (word, phoneme), user_input, ('Careful', correct_spell), 'Invalid entry')
    
    
    def test_invalid_entry(self):
        word = '/ʃɜ:t/'
        phoneme = '/ɜ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['3', 'run', correct_spell]
        
        self.help_patch(main.test_with_help, (word, phoneme), user_input, 'Invalid entry')
        
        
        
class TestFindHoms(BaseTest):
    """Test 'find_homs()' based on user input"""
    
    def test_all_guessed(self):
        phoneme = '/eə/'
        homoph = '/feə/'
        
        user_inputs = [['fair', 'fare'], ['fare', '3', 'run', 'fair']]
        
        for user_input in user_inputs:
            with self.subTest(user_input = user_input):
                all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
                self.help_patch(main.find_homs, (homoph, all_spellings), user_input, ('All done!', 'Yes!'))
                  
            
    def test_some_missing(self):
        phoneme = '/ɔ:/'
        homoph = '/ɔ:/'
        
        user_inputs = [['ore', 'or', 'orr', 'awr', 'auw'], ['auw', 'awe', 'orr','aur', 'awr'], ['or', 'ore', 'oar', 'aur', 'oor']]
        
        for user_input in user_inputs:
            with self.subTest(user_input = user_input):
                all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
                self.help_patch(main.find_homs, (homoph, all_spellings), user_input, ('The remaining homophones', 'Yes!'))
            
    
    def test_none_guessed(self):
        phoneme = '/eə/'
        homoph = '/heə/'
            
        user_input = ['her', 'herr', 'air', 'haer', 'heer']
        
        all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
        self.help_patch(main.find_homs, (homoph, all_spellings), user_input, 'All the homophones', 'Yes!')

        
    def test_invalid_entry(self):
        phoneme = '/ɔ:/'
        homoph = '/sɔ:/'
        
        user_input = ['saw', '4', '*/', 'soar', 'sore']
        
        all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
        self.help_patch(main.find_homs, (homoph, all_spellings), user_input, 'Only letters')
        
        
        
class TestUpdateAudio(unittest.TestCase):
    """Test the behaviour of 'update_audio()'.
    
    Despite the repetitive boilerplate code, subTest and a helper function are intentionally omitted as they would compromise readability."""

    @patch('main.save_progress')
    @patch('main.playsound')
    @patch('main.get_phoneme')
    def test_update_audio_no_audio(self, mock_get_phoneme, mock_playsound, mock_save):
        phoneme = '/i:/'
        seen = {phoneme: 'offline'}
        
        mock_get_phoneme.return_value = None
        with patch('sys.stdout', new_callable=StringIO) as fake:
            main.update_audio(phoneme, seen)
            output = fake.getvalue() 
            
        mock_playsound.assert_not_called()
        self.assertIn('audio unavailable', output)
        mock_save.assert_called_once_with(phoneme, seen, None)
        
    
    @patch('main.save_progress')
    @patch('main.playsound')
    @patch('main.get_phoneme')
    def test_update_audio_with_audio(self, mock_get_phoneme, mock_playsound, mock_save):
        phoneme = '/i:/'
        seen = {phoneme: 'offline'}
        
        mock_get_phoneme.return_value = '/path/e.mp3'
        audio = mock_get_phoneme.return_value
        with patch('sys.stdout', new_callable=StringIO) as fake:
            main.update_audio(phoneme, seen)
            output = fake.getvalue() 
        
        mock_playsound.assert_called_once_with(audio)
        self.assertNotIn('audio unavailable', output)
        mock_save.assert_called_once_with(phoneme, seen, audio)
        

if __name__ == '__main__':
    unittest.main()