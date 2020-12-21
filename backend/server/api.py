from pydantic import BaseModel
import numpy as np
from typing import *


class HashableBaseModel(BaseModel):
    def __hash__(self):
        return hash(self.json())

    @classmethod
    def validate(cls, v: np.ndarray):
        return v


class GoodbyePayload(HashableBaseModel):
    firstname: str


class TextPayload(HashableBaseModel):
    extracts: str
    quality: bool


class ImagePayload(HashableBaseModel):
    extract: str
    current: Optional[List[str]]


class FormPayload(HashableBaseModel):
    coherence: float
    clarity: float
    creativity: float
    freeForm: str
    html: str
