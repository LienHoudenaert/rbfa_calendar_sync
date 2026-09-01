from app import load_saved_teams, refresh_team_calendar


def main():

    teams = load_saved_teams()

    print(f"Found {len(teams)} saved teams.")

    for team in teams:

        team_id = team['id']

        print(
            f"Refreshing "
            f"{team['club']} - "
            f"{team['name']} "
            f"({team_id})"
        )

        try:

            refresh_team_calendar(team_id)

            print(
                f"Successfully refreshed {team_id}"
            )

        except Exception as exc:

            print(
                f"ERROR refreshing {team_id}: {exc}"
            )


if __name__ == '__main__':
    main()