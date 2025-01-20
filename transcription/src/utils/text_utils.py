import re
from typing import Optional
from deepmultilingualpunctuation import PunctuationModel

_model = PunctuationModel()


class TextFormatter:

    @staticmethod
    def format_transcript(text: str) -> str:
        return "" if not text else _model.restore_punctuation(text)(text)
