from datetime import datetime

from tasi.io import Position
from tasi.io.public.base import BaseModel


class SMOS(BaseModel):

    #: The SMOS value
    value: float
