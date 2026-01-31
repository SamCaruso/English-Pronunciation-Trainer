from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from phoneme_api import get_phoneme, AUDIO_DIR
import logic
from phonemes_dict import phonemes
import logging
import log_file
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import schemas as s
import time


logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware('http')
async def catch_all(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        raise 
    except Exception:
        return JSONResponse(status_code=500, content={'detail': 'Internal server error'})
    
    
app.add_middleware(  # Open CORS for development; restrict in production
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.mount('/audio', StaticFiles(directory=AUDIO_DIR), name='audio')


IDEMPOTENCY_STORE = {}
IDEMPOTENCY_DURATION = 6000

def clean_idempotency_store():
    now = time.time()
    expired = [key for key, value in IDEMPOTENCY_STORE.items() if now - value['time'] > IDEMPOTENCY_DURATION]
    for key in expired:
        IDEMPOTENCY_STORE.pop(key, None)
        

def check_idempotency(idempotency_key, user_input, function):
    clean_idempotency_store()
    
    if not idempotency_key:
        raise HTTPException(status_code=400, detail='Missing Idempotency-Key Header')
    
    store_idem_key = f'{function.__name__}:{idempotency_key}'
    cached = IDEMPOTENCY_STORE.get(store_idem_key)  #avoid accinetal same key
    if cached:
        return JSONResponse(status_code=cached['status'], content=cached['body'])

    result = function(user_input.model_dump())
    
    IDEMPOTENCY_STORE[store_idem_key] = {
        'time': time.time(),
        'status': 200,
        'body': result
    }
    
    return result


@app.get('/reviewstatus', response_model=s.ReviewResponse)
def start():
    phonemes_pool = logic.get_phonemes_pool()
    if not phonemes_pool:
        return {'status': s.ReviewStatus.REVIEW_ONLY} 
    if len(phonemes_pool) == len(phonemes):
        return {'status': s.ReviewStatus.NO_PROGRESS} 
    else:
        return {'status': s.ReviewStatus.REVIEW_LEARN} 

    
@app.get('/phonemescovered', response_model = list[s.PhonemesCoveredResponse])  
def phonemes_covered():
    seen = logic.phonemes_covered()
    return seen

    
@app.get('/reviewspell', response_model=list[s.SpellResponse])
def review_spelling():
    seen = logic.load_progress()
    return logic.review_spell(seen)

    
@app.get('/reviewhomoph', response_model=list[s.HomophResponse])
def review_homoph():
    seen = logic.load_progress()
    return logic.review_homophones(seen)
    
        
@app.get('/learn', response_model=s.LearnResponse)
def learn():
    phoneme, patterns = logic.patterns()
    logger.info(f'Starting learning process for phoneme {phoneme}')
    audio_file = get_phoneme(phonemes[phoneme]['api'])
    audio_url = f'/audio/{Path(audio_file).name}' if audio_file else None
    return {'phoneme': phoneme, 'ipa': f'/{phoneme}/', 'audio_url': audio_url, 'patterns': patterns}


@app.get('/spell/{phoneme}', response_model=list[s.SpellResponse])
def spell(phoneme: str):
    return logic.spell_learn(phoneme)


@app.get('/homophones/{phoneme}', response_model=list[s.HomophResponse])
def find_homophones(phoneme: str):
    return logic.homophones_learn(phoneme)


@app.post('/checkspellanswer', response_model=s.SpellAnswerResponse)
def check_spelling_answer(user_input: s.Answer,
                          idempotency_key: str = Header(None, alias='Idempotency-Key')):
    return check_idempotency(idempotency_key, user_input, logic.check_spell_answer)


@app.post('/checkhomophanswer', response_model=s.HomophAnswerResponse)
def check_homoph_answer(user_input: s.Answer,
                        idempotency_key: str = Header(None, alias='Idempotency-Key')):
    return check_idempotency(idempotency_key, user_input, logic.check_homophone_answer)


@app.post('/saveprogress', response_model = s.SaveProgressResponse)
def save(progress: s.SaveProgress):
    seen = logic.load_progress()
    return logic.save_progress(progress.model_dump(), seen)