import requests

DO_SEARCH_CLUB_HASH = "02ed5d3ff96be090db6c65abbcbb5a953788af5ca517ec0f8988137b5ce73345"
GET_CLUB_TEAMS_HASH = "79a7fb506ae28a8f7de7711dfa2dc37ac1cc8697798fe92b1ada0fffec2e6f22"
GET_TEAM_CALENDAR_HASH = "3f0441e6723b9852b4f0cff2c872f4aa674c5de2d23589efc70c7a4ffb7f6383"
GET_MATCH_DETAIL_HASH = "cd8867b845c206fe7aa75c1ebf7b53cbda0ff030253a45e2e2b4bcc13ee46c9a"

API_URL = "https://datalake-prod2018.rbfa.be/graphql"

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
               "sha256Hash": DO_SEARCH_CLUB_HASH
         }
      }
   }

   response = requests.post(api_url, json=params)
   if response.status_code == 200:
      return response.json()
   else:
      return None

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
               "sha256Hash": GET_CLUB_TEAMS_HASH
         }
      }
   }

   response = requests.post(api_url, json=params)
   if response.status_code == 200:
      return response.json()
   else:
      return None


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
               "sha256Hash": GET_TEAM_CALENDAR_HASH
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
               "sha256Hash": GET_MATCH_DETAIL_HASH
         }
      }
   }

   response = requests.post(api_url, json=params) 
   if response.status_code == 200:
      return response.json()
   else:
      return None