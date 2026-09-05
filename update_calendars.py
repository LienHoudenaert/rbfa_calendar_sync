from services.storage import load_saved_teams
from services.calendar import refresh_team_calendar
from services.git_backup import backup_synced_calendars


def main():
    teams = load_saved_teams()

    print(f"Found {len(teams)} saved teams.")

    for team in teams:
        team_id = team['id']

        print(
            f"Refreshing "
            f"{team['club']} - {team['name']} ({team_id})"
        )

        try:
            refresh_team_calendar(team_id)
            print(f"Successfully refreshed {team_id}")

        except Exception as exc:
            print(f"ERROR refreshing {team_id}: {exc}")


if __name__ == '__main__':
    main()

backup_synced_calendars()