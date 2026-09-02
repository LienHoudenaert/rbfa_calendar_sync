from flask import request

from config import LANGUAGES


def get_locale():
    language = request.cookies.get('frontend_lang')

    if language in LANGUAGES:
        return language

    return 'nl'