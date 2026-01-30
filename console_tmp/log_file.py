"""  
Logging module

This module configures logging for the project.
Since it is small and handled by me, the lowest level is intentionally set to logging.INFO.

encoding='utf-8' is included in the handler to make sure the logger correctly handles the phonetic symbols in the project.
"""

import logging 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def activate_handler(file = 'log_file.log'):
    handler = logging.FileHandler(file, encoding='utf-8')
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    
if not logger.handlers:
    activate_handler()