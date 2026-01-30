from pydantic import BaseModel, StrictInt, StrictStr, Field, ConfigDict
from enum import Enum
from typing import Optional, Literal, Union, Annotated


class ReviewStatus(str, Enum):
    REVIEW_ONLY = 'review_only'
    NO_PROGRESS = 'no_progress'
    REVIEW_LEARN = 'review_and_learn'
    
class ReviewResponse(BaseModel):
    status: ReviewStatus
    
    
    
class PhonemesCoveredResponse(BaseModel):
    phoneme: StrictStr
    audio_url: Optional[StrictStr] = None
    
    
    
class SpellResponse(BaseModel):
    word: StrictStr
    test_id: StrictStr
    options: tuple[StrictStr, StrictStr, StrictStr]
    
    

class HomophResponse(BaseModel):
    homoph: StrictStr
    test_id: StrictStr
    amount: StrictInt
    
    
    
class LearnResponse(BaseModel):
    phoneme: StrictStr
    ipa: StrictStr
    audio_url: Optional[StrictStr] = None
    patterns: dict[StrictStr, tuple[StrictStr, StrictStr]]
    
    
    
class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    test_id: StrictStr
    answer: StrictStr
    
class SpellAnswerCorrect(BaseModel):
    answered: Literal['correct']    
    
class SpellAnswerIncorrect(BaseModel):
    answered: Literal['incorrect']
    attempts_left: StrictInt
    
class SpellAnswerFailed(BaseModel):
    answered: Literal['failed']
    
class SpellAnswerFailedAll(BaseModel):
    answered: Literal['failed_all']
    solution: StrictStr
    
SpellAnswerResponse = Annotated[            
    Union[                         
      SpellAnswerCorrect,
      SpellAnswerIncorrect,
      SpellAnswerFailed, 
      SpellAnswerFailedAll],
    Field(discriminator='answered')     
]



class HomophAnswerCorrect(BaseModel):
    answered: Literal['correct']
    attempts_left: StrictInt

class HomophAnswerDone(BaseModel):
    answered: Literal['done']
    
class HomophAnswerIncorrect(BaseModel):
    answered: Literal['incorrect']
    attempts_left: StrictInt
    
class HomophAnswerFailed(BaseModel):
    answered: Literal['failed']
    solution: list[StrictStr]
    
class HomophAnswerFailedAll(BaseModel):
    answered: Literal['failed_all']
    solution: list[StrictStr]
    
HomophAnswerResponse = Annotated[
    Union[
        HomophAnswerCorrect,
        HomophAnswerDone,
        HomophAnswerIncorrect,
        HomophAnswerFailed, 
        HomophAnswerFailedAll],
    Field(discriminator='answered')
]