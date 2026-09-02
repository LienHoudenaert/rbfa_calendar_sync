from flask import Blueprint, render_template, request

from services.rbfa_api import get_teams_from_api


teams_bp = Blueprint('teams', __name__)


@teams_bp.route('/get_teams', methods=['POST'])
def get_teams():
    club_id = request.form['club_id']
    club_name = request.form['club_name']

    response = get_teams_from_api(club_id)
    results = response['data']['clubTeams']

    return render_template(
        'teams.html',
        club_name=club_name,
        team_results=results
    )