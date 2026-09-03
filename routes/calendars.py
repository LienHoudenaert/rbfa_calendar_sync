from flask import (
    Blueprint,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from services.storage import (
    team_is_saved,
    calendar_file_exists,
    save_team,
    load_saved_teams,
    ICAL_DIR,
)

from services.calendar import refresh_team_calendar
from services.git_backup import backup_new_calendar


calendars_bp = Blueprint('calendars', __name__)

@calendars_bp.route('/calendars')
def calendars():
    teams = load_saved_teams()

    return render_template(
        'calendars.html',
        teams=teams
    )

@calendars_bp.route('/get_team_calendar', methods=['POST'])
def get_team_calendar():
    team_id = request.form['team_id']
    team_name = request.form['team_name']
    club_name = request.form['club_name']
    club_logo = request.form['club_logo']

    if team_is_saved(team_id) and calendar_file_exists(team_id):
        ical_url = url_for(
            'calendars.serve_ical',
            filename=f'{team_id}.ics',
            _external=True
        )
    else:
        save_team(
            team_id=team_id,
            team_name=team_name,
            club_name=club_name,
            club_logo=club_logo
        )

        ical_url = refresh_team_calendar(team_id)

        # Backup newly created calendar to GitHub
        backup_new_calendar(f"{team_id}.ics")

    return render_template(
        'calendar.html',
        ical_link=ical_url,
        team_name=team_name,
        club_name=club_name,
        club_logo=club_logo
    )


@calendars_bp.route('/ical/<filename>')
def serve_ical(filename):
    response = send_from_directory(
        ICAL_DIR,
        filename,
        mimetype='text/calendar'
    )

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response