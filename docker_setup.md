# Docker Setup

This guide explains how to run RBFA Calendar Sync using Docker on a NAS or any Docker-compatible system.

The application uses two containers:

1. **rbfa-calendar** – Runs the Flask web application.
2. **rbfa-calendar-updater** – Periodically refreshes all saved calendars.

Both containers use the same application image and share the same persistent data directory.

---

# Architecture

```text
                    ┌─────────────────────────┐
                    │     RBFA Calendar       │
                    │       Web Container     │
                    │                         │
Browser ───────────►│  Flask + Gunicorn       │
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 │ Shared volume
                                 ▼
                    ┌─────────────────────────┐
                    │        /app/data        │
                    │                         │
                    │  teams.json             │
                    │  /ical/*.ics            │
                    └────────────┬────────────┘
                                 │
                                 │ Shared volume
                                 ▼
                    ┌─────────────────────────┐
                    │    Calendar Updater     │
                    │                         │
                    │ update_calendars.py     │
                    │                         │
                    └─────────────────────────┘
```

The shared data directory contains:

```text
data/
├── teams.json
└── ical/
    ├── team-id-1.ics
    ├── team-id-2.ics
    └── ...
```

This directory must persist outside the containers so calendars are not lost when containers are recreated or updated.

---

# Prerequisites

Your NAS must support Docker or Container Manager.

You will need:

* Docker / Docker Compose
* Git, or a downloaded copy of the repository
* A folder on the NAS for the application
* A persistent folder for calendar data

---

# 1. Create the Application Folder

Create a folder on your NAS.

For example:

```text
/docker/rbfa-calendar-sync
```

The final structure should look like this:

```text
rbfa-calendar-sync/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app.py
├── update_calendars.py
├── config.py
├── routes/
├── services/
├── templates/
├── static/
├── translations/
├── utils/
└── data/
```

---

# 2. Clone the Repository

If Git is available on your NAS:

```bash
git clone https://github.com/LienHoudenaert/rbfa_calendar_sync.git
```

Then enter the directory:

```bash
cd rbfa_calendar_sync
```

Alternatively, download the repository from GitHub and extract it into your Docker application folder.

---

# 3. Create the Persistent Data Folder

Make sure the following folder exists:

```text
data/
```

Inside it, create:

```text
data/
└── ical/
```

The complete structure becomes:

```text
rbfa-calendar-sync/
└── data/
    └── ical/
```

Docker will use this folder to persist:

* Saved teams
* Generated `.ics` calendar files

---

# 4. Dockerfile

The project uses the following `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/ical

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

This image is used by both containers.

---

# 5. Docker Compose Configuration

Use the following `docker-compose.yml`:

```yaml
services:

  rbfa-calendar:
    build: .
    container_name: rbfa-calendar
    restart: unless-stopped

    ports:
      - "8080:8080"

    volumes:
      - ./data:/app/data

    environment:
      TZ: Europe/Brussels


  rbfa-calendar-updater:
    build: .
    container_name: rbfa-calendar-updater
    restart: unless-stopped

    volumes:
      - ./data:/app/data

    environment:
      TZ: Europe/Brussels

    command: >
      sh -c "
      while true;
      do
        python update_calendars.py;
        sleep 21600;
      done
      "
```

---

# 6. Container Overview

## Web Application Container

Container name:

```text
rbfa-calendar
```

This container:

* Runs the Flask application
* Uses Gunicorn
* Listens on port `8080`
* Provides the web interface
* Creates calendar files
* Reads saved teams

Port mapping:

```yaml
ports:
  - "8080:8080"
```

The application will be available at:

```text
http://NAS-IP:8080
```

For example:

```text
http://192.168.1.100:8080
```

---

## Calendar Updater Container

Container name:

```text
rbfa-calendar-updater
```

This container:

* Runs in the background
* Executes `update_calendars.py`
* Loads all saved teams
* Refreshes every calendar
* Updates the `.ics` files

The updater runs every:

```text
21600 seconds
```

Which equals:

```text
6 hours
```

The relevant Docker command is:

```yaml
command: >
  sh -c "
  while true;
  do
    python update_calendars.py;
    sleep 21600;
  done
  "
```

---

# 7. Change the Update Interval

The update interval is controlled by:

```text
sleep 21600
```

Examples:

| Interval   | Seconds |
| ---------- | ------: |
| 30 minutes |    1800 |
| 1 hour     |    3600 |
| 3 hours    |   10800 |
| 6 hours    |   21600 |
| 12 hours   |   43200 |
| 24 hours   |   86400 |

For example, to update every hour:

```yaml
sleep 3600;
```

For every 12 hours:

```yaml
sleep 43200;
```

---

# 8. Start the Containers

From the project directory:

```bash
docker compose up -d --build
```

Docker will:

1. Build the application image.
2. Start the web application container.
3. Start the calendar updater container.

Check the running containers:

```bash
docker ps
```

You should see:

```text
rbfa-calendar
rbfa-calendar-updater
```

---

# 9. Access the Application

Open your browser and navigate to:

```text
http://NAS-IP:8080
```

For example:

```text
http://192.168.1.100:8080
```

---

# 10. View Container Logs

## Web Application Logs

```bash
docker logs rbfa-calendar
```

Follow the logs live:

```bash
docker logs -f rbfa-calendar
```

---

## Calendar Updater Logs

```bash
docker logs rbfa-calendar-updater
```

Follow the logs live:

```bash
docker logs -f rbfa-calendar-updater
```

The updater should display messages similar to:

```text
Found 3 saved teams.
Refreshing Club Name - Team Name (12345)
Successfully refreshed 12345
```

---

# 11. Restart the Containers

Restart both containers:

```bash
docker compose restart
```

Restart only the web application:

```bash
docker restart rbfa-calendar
```

Restart only the updater:

```bash
docker restart rbfa-calendar-updater
```

---

# 12. Stop the Containers

Stop both containers:

```bash
docker compose down
```

The persistent data remains available because it is stored in:

```text
./data
```

---

# 13. Update the Application

When a new version is available:

```bash
git pull
```

Then rebuild and restart the containers:

```bash
docker compose up -d --build
```

The existing calendars and saved teams remain available because the `data` directory is mounted as a persistent volume.

---

# 14. Persistent Data

The following Docker volume mapping is important:

```yaml
volumes:
  - ./data:/app/data
```

This means:

```text
NAS:
./data
```

is mapped to:

```text
Container:
/app/data
```

Both containers use the same data directory.

This allows:

```text
Web Container
     │
     │ creates calendar
     ▼
data/ical/team.ics
     ▲
     │ updates calendar
     │
Updater Container
```

Do not remove the `data` folder unless you want to delete all saved teams and calendars.

---

# 15. Recommended NAS Folder Structure

A recommended structure is:

```text
docker/
└── rbfa-calendar-sync/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── app.py
    ├── update_calendars.py
    ├── requirements.txt
    ├── routes/
    ├── services/
    ├── static/
    ├── templates/
    ├── translations/
    └── data/
        ├── teams.json
        └── ical/
```

---

# 16. Updating Through Portainer or Container Manager

If using a graphical Docker interface such as Portainer or Synology Container Manager:

1. Open the project or stack.
2. Pull the latest source code from GitHub.
3. Rebuild the containers.
4. Restart the stack.

The persistent `data` folder must remain mounted to:

```text
/app/data
```

for both containers.

---

# 17. Troubleshooting

## The website does not open

Check if the web container is running:

```bash
docker ps
```

Check the logs:

```bash
docker logs rbfa-calendar
```

Make sure port `8080` is not already used by another application.

---

## Calendars are not updating

Check the updater logs:

```bash
docker logs rbfa-calendar-updater
```

You can manually run the updater:

```bash
docker exec rbfa-calendar-updater python update_calendars.py
```

---

## Calendar data disappeared

Check whether the persistent volume is configured correctly:

```yaml
volumes:
  - ./data:/app/data
```

Both containers must use the same volume.

---

## Permission Problems

Make sure Docker has read and write access to:

```text
data/
```

and:

```text
data/ical/
```

---

# Summary

The application runs with two containers:

| Container               | Purpose                                     |
| ----------------------- | ------------------------------------------- |
| `rbfa-calendar`         | Runs the RBFA Calendar Sync web application |
| `rbfa-calendar-updater` | Periodically refreshes all saved calendars  |

Both containers share:

```text
./data:/app/data
```

Start everything with:

```bash
docker compose up -d --build
```

Access the application at:

```text
http://NAS-IP:8080
```

View the updater logs with:

```bash
docker logs -f rbfa-calendar-updater
```

This setup ensures that the web application is always available and saved calendars are automatically refreshed in the background.
