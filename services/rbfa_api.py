import requests
import logging

logger = logging.getLogger(__name__)

DO_SEARCH_CLUB_HASH = "02ed5d3ff96be090db6c65abbcbb5a953788af5ca517ec0f8988137b5ce73345"
GET_CLUB_TEAMS_HASH = "79a7fb506ae28a8f7de7711dfa2dc37ac1cc8697798fe92b1ada0fffec2e6f22"
GET_TEAM_CALENDAR_HASH = "3f0441e6723b9852b4f0cff2c872f4aa674c5de2d23589efc70c7a4ffb7f6383"
GET_MATCH_DETAIL_HASH = "cd8867b845c206fe7aa75c1ebf7b53cbda0ff030253a45e2e2b4bcc13ee46c9a"

API_URL = "https://datalake-prod2018.rbfa.be/graphql"
RBFA_URL = "https://www.rbfa.be/"

def create_rbfa_session():
   session = requests.Session()

   session.headers.update({
      "User-Agent": (
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
         "AppleWebKit/537.36 (KHTML, like Gecko) "
         "Chrome/153.0.0.0 Safari/537.36"
      ),
      "Accept": "*/*",
      "Accept-Language": "en-US,en;q=0.9",
      "Cache-Control": "no-cache",
      "Origin": "https://www.rbfa.be",
      "Pragma": "no-cache",
      "Referer": "https://www.rbfa.be/",
   })

   # Establish the normal RBFA website session first.
   response = session.get(
      "https://www.rbfa.be/",
      timeout=30,
   )
   
   response.raise_for_status()
   return session
   
rbfa_session = create_rbfa_session()

def graphql_request(payload):
   response = rbfa_session.post(
      API_URL,
      json=payload,
      timeout=30,
   )

   response.raise_for_status()
   data = response.json()
   
   if "errors" in data:
      logger.error("RBFA GraphQL error: %s", data["errors"])
      return None

   return data

def get_clubs_from_api(search):
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

   return graphql_request(params)


def get_teams_from_api(club_id):
   params = {
      "operationName": "getClubTeams",
      "variables": {
         "clubId": str(club_id),
         "language": "nl",
      },
      "extensions": {
         "persistedQuery": {
               "version": 1,
               "sha256Hash": GET_CLUB_TEAMS_HASH,
         }
      },
   }

   return graphql_request(params)


def get_team_calendar_from_api(team_id):
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

   return graphql_request(params)


def get_match_detail_from_api(match_id):
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

   return graphql_request(params)