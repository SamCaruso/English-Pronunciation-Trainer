# English Pronunciation Trainer

The web implementation lives in Web/ and is under active development.
Current focus is improving retry/restart behavior, followed by database integration and a TypeScript migration.

CURRENT FULLY-FUNCTIONAL IMPLEMENTATION:
A console-based Python app that helps users learn and memorise the most common spelling-pronunciation patterns of Standard British English phonemes (=sounds).  
Practice includes randomised spelling exercises, homophones, and audio playback through the Free Dictionary API.

---

## Features

- Learn one new phoneme at a time with example words.
- Spelling exercises with and without hints.
- Homophone drills to reinforce pronunciation patterns.
- Audio playback of phonemes (British English) via Free Dictionary API.
- Audio file saved to local directory for offline use and reduction of API calls.
- Saves progress in a JSON file for future review.
- Mandatory review of previously covered phonemes to promote gradual learning.
- Handles invalid inputs and missing audio (if none exists or simply the British version doesn't) gracefully.

---

## Dependencies

- requests -> fetch phoneme audio from the Free Dictionary API
- playsound (or playsound==1.2.2 to ensure compatibility across platforms) -> play phoneme audio

---

## Usage

Running the app on main.py will start the program
