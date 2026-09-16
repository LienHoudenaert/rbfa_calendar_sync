import time

from services.storage import load_saved_teams
from services.calendar import refresh_team_calendar
from services.git_backup import backup_synced_calendars


SYNC_DELAY_SECONDS = 60


def main():
    teams = load_saved_teams()

    print(f"Found {len(teams)} saved teams.")

    for index, team in enumerate(teams):
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


        # Wait before syncing the next calendar.
        # No need to wait after the final calendar.
        if index < len(teams) - 1:
            print(
                f"Waiting {SYNC_DELAY_SECONDS} seconds "
                "before the next calendar..."
            )
            time.sleep(SYNC_DELAY_SECONDS)


if __name__ == '__main__':
    main()

backup_synced_calendars()