from flask import Blueprint, render_template, redirect, request, url_for
from config import LANGUAGES

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/change_language/<lang_code>', methods=['GET'])
def change_language(lang_code):
    if lang_code not in LANGUAGES:
        lang_code = 'nl'

    next_page = request.args.get('next', '/')

    # /get_clubs is POST-only, so never redirect to it.
    if next_page == '/get_clubs' or next_page == '/get_teams' or next_page == '/get_team_calendar':
        next_page = '/'

    response = redirect(next_page)

    response.set_cookie(
        'frontend_lang',
        lang_code,
        max_age=60 * 60 * 24 * 365,
        httponly=True,
        samesite='Lax'
    )

    return response