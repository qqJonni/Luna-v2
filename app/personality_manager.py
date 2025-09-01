# app/personality_manager.py
from .generate import PERSONALITIES

def select_personality(age_preference: str = None, temperament: str = None) -> dict:
    """Выбирает персоналию на основе предпочтений пользователя"""
    if temperament == "дружелюбная":
        return PERSONALITIES["friendly"]
    elif temperament == "спокойная":
        return PERSONALITIES["calm"]
    elif age_preference == "старше":
        return PERSONALITIES["calm"]
    else:
        return PERSONALITIES["default"]