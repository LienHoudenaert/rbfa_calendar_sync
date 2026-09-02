import json
import os

DATA_DIR = 'data'
ICAL_DIR = os.path.join(DATA_DIR, 'ical')
TEAMS_FILE = os.path.join(DATA_DIR, 'teams.json')

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


def team_is_saved(team_id):
    teams = load_saved_teams()
    return any(str(team["id"]) == str(team_id) for team in teams)


def calendar_file_exists(team_id):
    return os.path.isfile(
        os.path.join(ICAL_DIR, f'{team_id}.ics')
    )