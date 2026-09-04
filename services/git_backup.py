import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRANCH = "updater"


def run_git_command(*args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def backup_new_calendar(calendar_filename):
    """
    Commit and push a newly created calendar and teams.json to GitHub.
    """

    try:
        # Stage the new calendar and teams.json
        run_git_command(
            "add",
            "data/teams.json",
            f"data/ical/{calendar_filename}",
        )

        # Check whether there are staged changes
        result = run_git_command(
            "diff",
            "--cached",
            "--quiet",
            check=False,
        )

        # Exit code 0 means no differences
        if result.returncode == 0:
            return False

        # Create commit
        run_git_command(
            "commit",
            "-m",
            "Update generated calendars",
        )

        # Push to GitHub
        run_git_command(
            "push",
            "origin",
            "main",
        )

        print(f"Git backup created for {calendar_filename}")

        return True

    except subprocess.CalledProcessError as error:
        print("Git backup failed:")
        print(error.stderr)

        return False