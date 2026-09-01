import os
import json
from flask import (
    Flask,
    render_template,
    request,
    Response,
    redirect,
    send_from_directory,
    url_for
   )
from icalendar import Calendar, Event
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from flask_babel import Babel
from flask_babel import gettext as _

DATA_DIR = 'data'
ICAL_DIR = os.path.join(DATA_DIR, 'ical')
TEAMS_FILE = os.path.join(DATA_DIR, 'teams.json')

LANGUAGES = {
    'en': 'English',
    'nl': 'Dutch'
}

doSearch_club_hash = "02ed5d3ff96be090db6c65abbcbb5a953788af5ca517ec0f8988137b5ce73345"
getClubTeams_hash = "79a7fb506ae28a8f7de7711dfa2dc37ac1cc8697798fe92b1ada0fffec2e6f22"
getTeamCalendar_hash = "3f0441e6723b9852b4f0cff2c872f4aa674c5de2d23589efc70c7a4ffb7f6383"
getMatchDetail_hash = "cd8867b845c206fe7aa75c1ebf7b53cbda0ff030253a45e2e2b4bcc13ee46c9a"

def ensure_data_directory():
   os.makedirs(ICAL_DIR, exist_ok=True)

   if not os.path.exists(TEAMS_FILE):
      with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
         json.dump(
               {"teams": []},
               f,
               indent=2,
               ensure_ascii=False
         )
         f.write('\n')


def load_saved_teams():
   ensure_data_directory()

   with open(TEAMS_FILE, 'r', encoding='utf-8') as f:
      data = json.load(f)

   return data.get('teams', [])


def save_team(team_id, team_name, club_name):
   ensure_data_directory()

   teams = load_saved_teams()

   team_id = str(team_id)

   # Don't add the same team twice.
   for team in teams:
      if str(team['id']) == team_id:
         return False

   teams.append({
      'id': team_id,
      'name': team_name,
      'club': club_name
   })

   teams.sort(key=lambda team: int(team['id']))

   with open(TEAMS_FILE, 'w', encoding='utf-8') as f:
      json.dump(
         {'teams': teams},
         f,
         indent=2,
         ensure_ascii=False
      )
      f.write('\n')

   return True

def get_locale():
   language = request.cookies.get('frontend_lang')

   if language in LANGUAGES:
      return language

   return request.accept_languages.best_match(
      LANGUAGES.keys()
   ) or 'en'

app = Flask(__name__)

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app, locale_selector=get_locale)

app.jinja_env.globals['get_locale'] = get_locale

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/change_language/<lang_code>', methods=['GET'])
def change_language(lang_code):
   if lang_code not in LANGUAGES:
      lang_code = 'en'

   response = redirect(request.referrer or url_for('index'))

   response.set_cookie(
      'frontend_lang',
      lang_code,
      max_age=60 * 60 * 24 * 365,
      httponly=True,
      samesite='Lax'
   )

   return response

@app.route('/get_clubs', methods=['POST'])
def get_club():
   club_name = request.form['club_name']
   response = get_clubs_from_api(club_name)
   print(response)
   results = response['data']['search']['results']
   return render_template('clubs.html', search=club_name, club_results=results)

def get_clubs_from_api(search):

   api_url = "https://datalake-prod2018.rbfa.be/graphql"
   params = {
      "operationName": "DoSearch",
      "variables": {
         "first": 6,
         "offset": 0,
         "filter": {
               "query": search,
               "type": "club"
         },
         "language": "nl",
         "channel": "belgianfootball",
         "location": "BE"
      },
      "extensions": {
         "persistedQuery": {
               "version": 1,
               "sha256Hash": doSearch_club_hash
         }
      }
   }

   response = requests.post(api_url, json=params)
   if response.status_code == 200:
      return response.json()
   else:
      return None
   
@app.route('/get_teams', methods=['POST'])
def get_teams():
   club_id = request.form['club_id']
   club_name = request.form['club_name']
   response = get_teams_from_api(club_id)
   results = response['data']['clubTeams']
   return render_template('teams.html', club_name=club_name, team_results=results)

def get_teams_from_api(club_id):
   api_url = "https://datalake-prod2018.rbfa.be/graphql"
   params = {
      "operationName": "getClubTeams",
      "variables": {
         "clubId": str(club_id),
         "language": "nl"
      },
      "extensions": {
         "persistedQuery": {
               "version": 1,
               "sha256Hash": getClubTeams_hash
         }
      }
   }

   response = requests.post(api_url, json=params)
   if response.status_code == 200:
      return response.json()
   else:
      return None
   
@app.route('/get_team_calendar', methods=['POST'])
def get_team_calendar():

   team_id = request.form['team_id']
   team_name = request.form['team_name']
   club_name = request.form['club_name']

   # Save the team.
   save_team(
      team_id=team_id,
      team_name=team_name,
      club_name=club_name
   )

   # Generate the calendar immediately.
   ical_url = refresh_team_calendar(team_id)

   return render_template(
      'calendar.html',
      ical_link=ical_url,
      team_name=team_name,
      club_name=club_name
   )


def refresh_team_calendar(team_id):
   """
   Fetch the latest calendar from RBFA and regenerate the .ics file.
   Returns the public URL of the generated calendar.
   """

   response = get_team_calendar_from_api(team_id)

   if not response:
      raise RuntimeError(f"Could not fetch calendar for team {team_id}")

   results = response['data']['teamCalendar']

   calendar_items = []

   for match in results:
      match_id = match['id']

      match_response = get_match_detail_from_api(match_id)

      if not match_response:
         print(f"Could not fetch match details for {match_id}")
         continue

      match_detail = match_response['data']['matchDetail']

      match_name = (
         match_detail['homeTeam']['name']
         + ' - '
         + match_detail['awayTeam']['name']
      )

      match_date_start = match_detail['startTime']

      match_type = match_detail['eventType']

      match_location = (
         f"{match_detail['location']['address']}, "
         f"{match_detail['location']['postalCode']} "
         f"{match_detail['location']['city']}"
      )

      match_terrain_type = (
         'Kunstgras'
         if match_detail['location']['synthetic']
         else 'Gras'
      )

      match_outcome = (
         f"{match_detail['outcome']['homeTeamGoals']} - "
         f"{match_detail['outcome']['awayTeamGoals']}"
         if match_detail['outcome']['isFinished']
         else ""
      )

      calendar_items.append({
         'id': match_id,
         'name': match_name,
         'start_date': match_date_start,
         'type': match_type,
         'location': match_location,
         'terrain_type': match_terrain_type,
         'outcome': match_outcome,
      })

   return generate_ical_feed(calendar_items, team_id)

def get_team_calendar_from_api(team_id):
   api_url = "https://datalake-prod2018.rbfa.be/graphql"
   params = {
      "operationName": "GetTeamCalendar",
      "variables": {
         "teamId": str(team_id),
         "language": "nl",
         "sortByDate": "asc"
      },
      "extensions": {
         "persistedQuery": {
               "version": 1,
               "sha256Hash": getTeamCalendar_hash
         }
      }
   }

   response = requests.post(api_url, json=params)   
   if response.status_code == 200:
      return response.json()
   else:
      return None
   
def get_match_detail_from_api(match_id):
   api_url = "https://datalake-prod2018.rbfa.be/graphql"
   params = {
      "operationName": "GetMatchDetail",
      "variables": {
         "matchId": str(match_id),
         "language": "nl"
      },
      "extensions": {
         "persistedQuery": {
               "version": 1,
               "sha256Hash": getMatchDetail_hash
         }
      }
   }

   response = requests.post(api_url, json=params) 
   if response.status_code == 200:
      return response.json()
   else:
      return None

@app.route('/calendars')
def calendars():

   teams = load_saved_teams()

   return render_template(
      'calendars.html',
      teams=teams
   )
   
def generate_ical_feed(calendar_items, team_id):
   file_name = f"{team_id}.ics"
   cal = Calendar()
   cal.add('prodid', '-//LienHoudenaert//RBFACalendarSync//NL')
   cal.add('version', '2.0')
   cal.add('tzid', 'Europe/Brussels')
   cal.add('timezone-id', 'Europe/Brussels')
   cal.add('x-wr-timezone', 'Europe/Brussels')
   for item in calendar_items:
      extra_info = f"Terrein: {item['terrain_type']}\nType: {item['type']}\nEindstand: {item['outcome']}"
      # Create an Event object for each event
      event_obj = Event()
      event_obj.add('uid', f"{item['id']}@rbfa-calendar-sync.app")
      event_obj.add('summary', item['name'])
      event_obj.add('dtstamp', datetime.now(timezone.utc))
      start = datetime.strptime(
         item['start_date'],
         "%Y-%m-%dT%H:%M:%S"
      ).replace(tzinfo=ZoneInfo("Europe/Brussels"))

      end = start + timedelta(hours=1, minutes=45)

      event_obj.add('dtstart', start)
      event_obj.add('dtend', end)
      event_obj.add('location', item['location'])
      event_obj.add('description', extra_info)
      
      # Add the event to the calendar
      cal.add_component(event_obj)

   file_path = os.path.join(
      ICAL_DIR,
      file_name
   )

   with open(file_path, 'wb') as f:
      f.write(cal.to_ical())

   # IMPORTANT:
   # This URL is now served by our Flask application.
   return url_for(
      'serve_ical',
      filename=file_name,
      _external=True
   )

@app.route('/ical/<filename>')
def serve_ical(filename):
   response = send_from_directory(
      ICAL_DIR,
      filename,
      mimetype='text/calendar'
   )

   # Don't let a browser/proxy keep an old copy forever.
   response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
   response.headers['Pragma'] = 'no-cache'
   response.headers['Expires'] = '0'

   return response

if __name__ == '__main__':
    app.run(debug=True)