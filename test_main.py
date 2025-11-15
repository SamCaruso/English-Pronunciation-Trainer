"""
Testing module for main.py

Since this is a simple input-cased console app, I mock json file handling and a couple of user-input functions, 
but I intentionally omit further testing as it would be trivial and repetitive for this type of app

"""


import unittest
from unittest.mock import patch, Mock, mock_open
import json
import main
from io import StringIO


class TestJson(unittest.TestCase):
    """Test creation, saving and loading of a json file for progress"""
    
    def test_load_progress_with_file(self):
        mock_data = json.dumps({'Phonemes seen' : ['/eə/']})
        
        with patch('builtins.open', mock_open(read_data = mock_data)):
            seen = main.load_progress()
            
        self.assertEqual(seen, ['/eə/'])
        
        
    def test_load_progress_no_file(self):
        with patch('builtins.open', side_effect = FileNotFoundError):
            seen = main.load_progress()
            
        self.assertEqual(seen, [])
    

    def test_save_progress(self):
        
        cases = [
            ('/ɔ:/', ['/ɔ:/', '/ɜ:/', '/eə/'], {'Phonemes seen' : ['/ɔ:/', '/ɜ:/', '/eə/']}), 
            ('/ɜ:/', [], {'Phonemes seen' : ['/ɜ:/']}), 
            ('/eə/', ['/ɔ:/', '/ɜ:/'], {'Phonemes seen' : ['/ɔ:/', '/ɜ:/', '/eə/']})
            ]
        
        for phoneme, initial_seen, final_seen in cases:
            with self.subTest(phoneme = phoneme, initial_seen = initial_seen, final_seen = final_seen):
                m = mock_open()
                with patch('builtins.open', m):
                    main.save_progress(phoneme, initial_seen)
                    
                    written = "".join(call.args[0] for call in m().write.call_args_list)
                    self.assertEqual(json.loads(written), final_seen)
                    

class TestLearn(unittest.TestCase):
    """Test behaviour of 'learn()'"""
    
    @patch('main.get_phoneme')
    def test_learn(self, mock_get):
        
        cases = [('/ɔ:/', True), ('/ɜ:/', False)]
        
        for phoneme, api in cases:
            with self.subTest(phoneme = phoneme, api = api):
                mock_get.return_value = api
                
                with patch('sys.stdout', new_callable=StringIO):
                    pron = main.learn(phoneme)
                
                self.assertEqual(pron, api)
                mock_get.assert_called_once_with(main.phonemes[phoneme]['api'])
                
                mock_get.reset_mock()
        

class TestWithHelp(unittest.TestCase):
    """Test behaviour of 'test_with_help()' based on user input.
    
    subTest is intentionally omitted to promote readability: grouping all these cases together under a single subTest 
    would create too many variables to unpack"""
    
    def test_correct_first_attempt(self):
        word = '/leə/'
        phoneme = '/eə/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        with patch('builtins.input', side_effect = [correct_spell]):
              with patch('sys.stdout', new_callable=StringIO) as fake:
                  main.test_with_help(word, phoneme)
                  output = fake.getvalue()
    
        self.assertIn('Yes!', output)
        self.assertNotIn('Invalid entry', output)
    
                    
    def test_fail_then_correct(self):
        word = '/wɜ:m/'
        phoneme = '/ɜ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['warm', correct_spell]
        
        with patch('builtins.input', side_effect=user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                main.test_with_help(word, phoneme)
                output = fake.getvalue()
                
        self.assertIn('Yes!', output)
        self.assertNotIn('Invalid entry', output)
        
        
    def test_fail_both_valid_entries(self):
        word = "/'ɔ:də/"
        phoneme = '/ɔ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['awder', 'aurder']
        
        with patch('builtins.input', side_effect = user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                main.test_with_help(word, phoneme)
                output = fake.getvalue()
                
        self.assertIn('Careful', output)
        self.assertNotIn('Invalid entry', output)
        
    
    def test_invalid_entry(self):
        word = '/ʃɜ:t/'
        phoneme = '/ɜ:/'
        correct_spell = main.phonemes[phoneme]['spelling'][word][0]
        
        user_input = ['3', 'run', correct_spell]
        
        with patch('builtins.input', side_effect = user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                main.test_with_help(word, phoneme)
                output = fake.getvalue()
                
        self.assertIn('Invalid entry', output)
        
        
class TestFindHoms(unittest.TestCase):
    """Test 'find_homs()' based on user input"""
    
    def test_all_guessed(self):
        phoneme = '/eə/'
        homoph = '/feə/'
        
        user_inputs = [['fair', 'fare'], ['fare', '3', 'run', 'fair']]
        
        for user_input in user_inputs:
            with self.subTest(user_input = user_input):
                all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
                with patch('builtins.input', side_effect = user_input):
                    with patch('sys.stdout', new_callable=StringIO) as fake:
                        main.find_homs(homoph, all_spellings)
                        output = fake.getvalue()
            
                self.assertIn('Yes!', output)
                self.assertIn('All done!', output)
            
            
    def test_some_missing(self):
        phoneme = '/ɔ:/'
        homoph = '/ɔ:/'
        
        user_inputs = [['ore', 'or', 'orr', 'awr', 'auw'], ['auw', 'awe', 'orr','aur', 'awr'], ['or', 'ore', 'oar', 'aur', 'oor']]
        
        for user_input in user_inputs:
            with self.subTest(user_input = user_input):
                all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
                with patch('builtins.input', side_effect = user_input):
                    with patch('sys.stdout', new_callable=StringIO) as fake:
                        main.find_homs(homoph, all_spellings)
                        output = fake.getvalue()
                        
                self.assertIn('Yes!', output)
                self.assertIn('The remaining homophones', output)   
            
    
    def test_none_guessed(self):
        phoneme = '/eə/'
        homoph = '/heə/'
            
        user_input = ['her', 'herr', 'air', 'haer', 'heer']
        
        all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
        with patch('builtins.input', side_effect = user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                    main.find_homs(homoph, all_spellings)
                    output = fake.getvalue()
                    
        self.assertIn('All the homophones', output)
        self.assertNotIn('Yes!', output)
        
    
    def test_invalid_entry(self):
        phoneme = '/ɔ:/'
        homoph = '/sɔ:/'
        
        user_input = ['saw', '4', '*/', 'soar', 'sore']
        
        all_spellings = main.phonemes[phoneme]['homophones'][homoph].copy()
        with patch('builtins.input', side_effect = user_input):
            with patch('sys.stdout', new_callable=StringIO) as fake:
                    main.find_homs(homoph, all_spellings)
                    output = fake.getvalue()
        
        self.assertIn('Only letters', output)



if __name__ == '__main__':
    unittest.main()