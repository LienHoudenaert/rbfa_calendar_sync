import os

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar, Event
from flask import url_for

from services.rbfa_api import (
    get_team_calendar_from_api,
    get_match_detail_from_api,
)

from services.storage import ICAL_DIR

BRUSSELS = ZoneInfo("Europe/Brussels")
DEFAULT_MATCH_DURATION = timedelta(hours=1, minutes=45)

def refresh_team_calendar(team_id):
    """
    Fetch the latest calendar from RBFA and regenerate the .ics file.
    Returns the public URL of the generated calendar.
    """

    response = get_team_calendar_from_api(team_id)

    if not response:
        raise RuntimeError(f"Could not fetch calendar for team {team_id}")

    results = response["data"]["teamCalendar"]

    calendar_items = []

    for match in results:
        match_id = match["id"]

        match_response = get_match_detail_from_api(match_id)

        if not match_response:
            print(f"Could not fetch match details for {match_id}")
            continue

        match_detail = match_response["data"]["matchDetail"]

        match_name = (
            match_detail["homeTeam"]["name"] + " - " + match_detail["awayTeam"]["name"]
        )

        match_date_start = match_detail["startTime"]

        location = match_detail.get("location") or {}
        address = location.get("address", "")
        postal_code = location.get("postalCode", "")
        city = location.get("city", "")

        match_location = (
            f"{address}, "
            f"{postal_code} "
            f"{city}"
        )

        match_terrain_type = ""
        if location.get("synthetic", False):
            match_terrain_type = 'Kunstgras'
        else:
            match_terrain_type = 'Gras'

        event_type = match_detail.get('eventType', "")
        match_type = ""
        if event_type == 'championship':
            match_type = 'Competitie'
        elif event_type == 'cup':
            match_type = 'Beker'
        else:
            match_type = 'Vriendschappelijk'

        outcome = match_detail.get('outcome') or {}
        match_outcome = ""
        if outcome.get('isFinished', False):
            home_goals = match_detail.get('homeTeamGoals', "")
            away_goals = match_detail.get('awayTeamGoals', "")
            if home_goals and away_goals:
                match_outcome = (
                    f"{home_goals} - "
                    f"{away_goals}"
                )

        calendar_items.append(
            {
                "id": match_id,
                "name": match_name,
                "start_date": match_date_start,
                "type": match_type,
                "location": match_location,
                "terrain_type": match_terrain_type,
                "outcome": match_outcome,
            }
        )

    return generate_ical_feed(calendar_items, team_id)


def generate_ical_feed(calendar_items, team_id):
    file_name = f"{team_id}.ics"
    cal = Calendar()

    cal.add("prodid", "-//RBFA Calendar Sync//NL")
    cal.add("version", "2.0") 
    cal.add("X-WR-TIMEZONE", "Europe/Brussels")
    for item in calendar_items:
        extra_info = f"Terrein: {item['terrain_type']}\nType wedstrijd: {item['type']}\nEindstand: {item['outcome']}"
        # Create an Event object for each event
        event_obj = Event()
        event_obj.add("uid", f"{item['id']}@rbfa-calendar-sync.app")
        event_obj.add("summary", item["name"])
        event_obj.add("dtstamp", datetime.now(timezone.utc))

        # RBFA startTime is already Belgian local time. 
        # # We are NOT converting the time. 
        start = datetime.strptime(item["start_date"], "%Y-%m-%dT%H:%M:%S", ).replace(tzinfo=BRUSSELS) 
        end = start + DEFAULT_MATCH_DURATION

        event_obj.add("dtstart", start)
        event_obj.add("dtend", end)
        event_obj.add("location", item["location"])
        event_obj.add("description", extra_info)

        # Add the event to the calendar
        cal.add_component(event_obj)

    file_path = os.path.join(ICAL_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(cal.to_ical())

    # IMPORTANT:
    # This URL is now served by our Flask application.
    return url_for("calendars.serve_ical", filename=file_name, _external=True)
