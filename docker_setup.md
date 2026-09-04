# Docker Setup on Synology NAS

This guide explains how to deploy RBFA Calendar Sync on a Synology NAS using Docker and Docker Compose.

The application consists of two containers:

- `rbfa-calendar` — the Flask web application.
- `rbfa-calendar-updater` — periodically updates all saved calendars.

---

# 1. Prerequisites

Before starting, make sure the following are available on your Synology NAS:

- Container Manager / Docker
- SSH enabled
- Git installed
- Docker Compose available

## Enable SSH

In DSM:

```text
Control Panel → Terminal & SNMP → Enable SSH service
```

Connect to the NAS:

```bash
ssh <username>@<NAS-IP>
```

---

# 2. Install Git

Git may not be installed by default.

Check:

```bash
git --version
```

If you receive:

```text
-sh: git: command not found
```

install Git using Synology Package Center.

After installation, reconnect through SSH and verify:

```bash
git --version
```

---

# 3. Clone the repository

Create the Docker directory:

```bash
mkdir -p /volume1/docker/rbfa-calendar-sync
```

Navigate to it:

```bash
cd /volume1/docker/rbfa-calendar-sync
```

Clone the repository:

```bash
git clone https://github.com/LienHoudenaert/rbfa_calendar_sync.git .
```

---

# 4. Docker Compose command on Synology

Depending on your Synology installation, the modern command:

```bash
docker compose
```

may not be available.

If you receive:

```text
docker: 'compose' is not a docker command.
```

use:

```bash
docker-compose
```

Examples:

```bash
docker-compose config
docker-compose build
docker-compose up -d
docker-compose ps
```

---

# 5. Configure the `.env` file

The application can automatically commit newly created calendars and `teams.json` to GitHub as a backup.

Create the `.env` file:

```bash
nano .env
```

If `nano` is not available, use:

```bash
vi .env
```

Add:

```env
GIT_REPO_URL=https://github.com/LienHoudenaert/rbfa_calendar_sync.git
GIT_BRANCH=main
GIT_USER_NAME=RBFA Calendar Sync
GIT_USER_EMAIL=your-email@example.com
GITHUB_TOKEN=YOUR_GITHUB_TOKEN
```

Make sure `.gitignore` contains:

```gitignore
.env
```

> Never commit or share your GitHub token.

---

# 6. Docker Compose configuration

The application uses two containers.

Example `docker-compose.yml`:

```yaml
services:
  rbfa-calendar:
    build: .
    container_name: rbfa-calendar
    restart: unless-stopped

    network_mode: host

    volumes:
      - ./data:/app/data

    environment:
      TZ: Europe/Brussels
      GIT_REPO_URL: ${GIT_REPO_URL}
      GIT_BRANCH: ${GIT_BRANCH:-main}
      GIT_USER_NAME: ${GIT_USER_NAME}
      GIT_USER_EMAIL: ${GIT_USER_EMAIL}
      GITHUB_TOKEN: ${GITHUB_TOKEN}

  rbfa-calendar-updater:
    build: .
    container_name: rbfa-calendar-updater
    restart: unless-stopped

    network_mode: host

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

# 7. Validate the Docker Compose file

Before building, validate the YAML:

```bash
docker-compose config
```

---

# 8. Docker permissions on Synology

Your SSH user may not have permission to access Docker.

You may encounter:

```text
PermissionError: [Errno 13] Permission denied
```

when running:

```bash
docker-compose build
```

Use `sudo`:

```bash
sudo docker-compose build
```

For Docker commands, use:

```bash
sudo docker-compose ...
```

Examples:

```bash
sudo docker-compose build
sudo docker-compose up -d
sudo docker-compose down
sudo docker-compose ps
sudo docker-compose logs
```

---

# 9. Configure the application port

Because the containers use:

```yaml
network_mode: host
```

the application port is directly exposed on the NAS.

For this setup, port `8081` is used.

The Dockerfile should run Gunicorn on:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "app:app"]
```

---

# 10. Build the containers

Navigate to the project directory:

```bash
cd /volume1/docker/rbfa-calendar-sync
```

Build:

```bash
sudo docker-compose build
```

---

# 11. Start the containers

Start both containers:

```bash
sudo docker-compose up -d
```

Check their status:

```bash
sudo docker-compose ps
```

Or:

```bash
sudo docker ps --format "table {{.Names}}\t{{.Ports}}"
```

Expected containers:

```text
rbfa-calendar
rbfa-calendar-updater
```

---

# 12. Check the application locally

Because host networking is used and Gunicorn runs on port `8081`, the application should be available at:

```text
http://NAS_IP:8081
```

Replace `NAS_IP` with your NAS IP address if necessary.

Always test this local URL before configuring the public domain.

---

# 13. Synology Reverse Proxy

The application can be exposed publicly through Synology Reverse Proxy.

## Create a Reverse Proxy rule

In DSM:

```text
Control Panel
→ Login Portal
→ Advanced
→ Reverse Proxy
```

Create a new rule.

### General

Name:

```text
RBFA Calendar Sync
```

### Source

```text
Protocol: HTTPS
Hostname: rbfa-calendar-sync.<DDNS>
Port: 443
```

### Destination

```text
Protocol: HTTP
Hostname: <NAS_IP>
Port: 8081
```

Traffic flow:

```text
Internet
    ↓
https://rbfa-calendar-sync.<DDNS>
    ↓
Synology Reverse Proxy
    ↓
http://<NAS_IP>:8081
    ↓
RBFA Calendar Sync
```

---

# 14. HTTPS Certificate

The hostname requires a valid SSL certificate.

In DSM:

```text
Control Panel
→ Security
→ Certificate
```

Add or request a Let's Encrypt certificate for:

```text
rbfa-calendar-sync.<DDNS>
```

---


# 15. Test the backend before testing the domain

First test:

```text
http://<NAS_IP>:8081
```

If this works, Docker and Flask are working correctly.

Then test:

```text
https://rbfa-calendar-sync.<DDNS>
```

If the local URL works but the public domain does not, the issue is with DNS, certificates, or the Synology Reverse Proxy configuration.

---

# 16. View logs

## Web application

```bash
sudo docker-compose logs -f rbfa-calendar
```

Last 50 lines:

```bash
sudo docker-compose logs --tail=50 rbfa-calendar
```

## Calendar updater

```bash
sudo docker-compose logs -f rbfa-calendar-updater
```

Last 50 lines:

```bash
sudo docker-compose logs --tail=50 rbfa-calendar-updater
```

---

# 17. Verify shared data

Both containers share:

```text
./data:/app/data
```

Check the web container:

```bash
sudo docker-compose exec rbfa-calendar ls -la /app/data
```

Check the updater:

```bash
sudo docker-compose exec rbfa-calendar-updater ls -la /app/data
```

Both should see the same calendar files and `teams.json`.

---

# 18. Updating the application

Navigate to the project directory:

```bash
cd /volume1/docker/rbfa-calendar-sync
```

Pull the latest changes:

```bash
git pull
```

Rebuild and restart:

```bash
sudo docker-compose up -d --build
```

---

# 19. Restarting the application

Restart everything:

```bash
sudo docker-compose restart
```

Restart only the web application:

```bash
sudo docker-compose restart rbfa-calendar
```

Restart only the updater:

```bash
sudo docker-compose restart rbfa-calendar-updater
```

---

# 20. Stopping the application

Stop the containers:

```bash
sudo docker-compose down
```

The data remains intact because it is stored in:

```text
/volume1/docker/rbfa-calendar-sync/data
```

---

# 21. Automatic calendar updates

The updater runs:

```bash
python update_calendars.py
```

every:

```text
21600 seconds
```

which equals:

```text
6 hours
```

---

# 22. Git backup

When a new calendar is created, the application can automatically:

1. Save the `.ics` calendar file.
2. Update `teams.json`.
3. Create a Git commit.
4. Push the changes to GitHub.

Commit messages follow:

```text
Added calendar <calendar-file-name>
```

This provides an additional backup outside the NAS.

Important data:

```text
data/
├── teams.json
└── *.ics
```

---

# 23. Useful commands

### Check running containers

```bash
sudo docker ps
```

### Check Docker Compose status

```bash
sudo docker-compose ps
```

### View logs

```bash
sudo docker-compose logs -f
```

### Rebuild everything

```bash
sudo docker-compose up -d --build
```

### Stop everything

```bash
sudo docker-compose down
```

### Restart everything

```bash
sudo docker-compose restart
```

### Validate Compose configuration

```bash
sudo docker-compose config
```

---

# Final Architecture

```text
                         Internet
                            │
                            ▼
        rbfa-calendar-sync.<DDNS>
                            │
                         HTTPS :443
                            │
                            ▼
                 Synology Reverse Proxy
                            │
                            ▼
                    HTTP <NAS_IP>:8081
                            │
                            ▼
                 ┌──────────────────────┐
                 │ RBFA Calendar Sync   │
                 │ Docker Container     │
                 │ network_mode: host   │
                 │ Gunicorn :8081       │
                 └──────────────────────┘
                            │
                            ▼
                     Shared data folder
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
      Calendar files                  teams.json
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                   GitHub Backup Repository


                 ┌──────────────────────┐
                 │ Calendar Updater     │
                 │ Docker Container     │
                 │ Runs every 6 hours   │
                 └──────────────────────┘
```

# Current Configuration Summary

| Component | Configuration |
|---|---|
| NAS project path | `/volume1/docker/rbfa-calendar-sync` |
| Docker command | `docker-compose` |
| Docker permissions | Use `sudo` |
| Web container | `rbfa-calendar` |
| Updater container | `rbfa-calendar-updater` |
| Network mode | `host` |
| Application port | `8081` |
| Local URL | `http://<NAS_IP>:8081` |
| Public URL | `https://rbfa-calendar-sync.<DDNS>` |
| Update interval | Every 6 hours |
| Shared data | `./data:/app/data` |
