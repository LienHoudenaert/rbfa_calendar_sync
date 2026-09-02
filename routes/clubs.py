from flask import Blueprint, render_template, request

from services.rbfa_api import get_clubs_from_api


clubs_bp = Blueprint('clubs', __name__)


@clubs_bp.route('/get_clubs', methods=['POST'])
def get_club():
    club_name = request.form['club_name']

    response = get_clubs_from_api(club_name)
    results = response['data']['search']['results']

    return render_template(
        'clubs.html',
        search=club_name,
        club_results=results
    )