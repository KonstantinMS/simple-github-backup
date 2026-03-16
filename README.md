# GitHub Backup Scheduler
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


Automated backup tool for GitHub repositories (public and private) with flexible scheduling.
Backup all repositories of a user or organization as mirror clones. Supports both interval-based and weekday/time-based scheduling with local timezone awareness.

# Features
- 🔄 Full mirror backups – clones everything (all branches, tags, refs) using git clone --mirror.

- 🔐 Private repository support – use a GitHub personal access token.

- 📅 Flexible scheduling:

- - Run every N hours.

- - Run on specific weekdays at a given time (e.g., every Monday and Thursday at 02:30).

- ⏱️ Local timezone – respects your system time.

- 📁 Automatic dated backup folders – default backup directory includes today's date.

- 🧩 Simple and maintainable – two clean Python scripts with minimal dependencies.

# Requirements
- Python 3.6 or higher

- git command-line tool installed and accessible in PATH

- requests library (install via pip)

# Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/github-backup-scheduler.git
cd github-backup-scheduler
```
2. Install Python dependencies:
```bash
pip install requests
```
3. (Optional) Make the scripts executable (for Linux systems):
```bash
chmod +x backup_github.py scheduler.py
```
# Configuration
To back up private repositories, you need a GitHub personal access token:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic).

2. Generate a new token with at least the repo scope (for full access to private repos) or public_repo for only public ones.

3. Set the token as an environment variable or pass it directly via the --token argument.

## Environment variable (recommended):
```bash
export GITHUB_TOKEN="your_token_here"
```
# Usage
# 1 Backup script (backup_github.py)
This script clones/updates all repositories of a given GitHub user or organization.
```bash
python backup_github.py USERNAME [BACKUP_DIR] [--token TOKEN]
```
- USERNAME – GitHub username or organization name.

- BACKUP_DIR – target directory (optional). If omitted, creates ./github_backup_YYYY-MM-DD.

- --token – GitHub token (optional, overrides environment variable).
## Examples:
```bash
# Backup public repos of 'octocat' to a dated folder
python backup_github.py octocat

# Backup including private repos, specify token and custom folder
python backup_github.py mycompany /mnt/backup/github --token ghp_abc123
```
## Scheduler script (scheduler.py)
This script runs the backup automatically according to a schedule.
```bash
python scheduler.py [--interval HOURS | --weekdays DAYS --time HH:MM] [other_args]
```
- --interval – run every N hours (e.g., --interval 12).

- --weekdays – comma‑separated list of weekdays (e.g., mon,wed,fri).
Supported: Russian (пн,вт,ср,чт,пт,сб,вс) or English (mon,tue,wed,thu,fri,sat,sun).

- --time – time of day in HH:MM format (24-hour). Required together with --weekdays.

- other_args – all remaining arguments are passed directly to backup_github.py (e.g., username, backup_dir, --token).
If neither --interval nor --weekdays+--time are given, the scheduler defaults to --interval 24.
## Examples:
- **Every 6 hours:**
```bash
python scheduler.py --interval 6 octocat
```
- **Every Monday and Thursday at 02:30 (local time):**
```bash
python scheduler.py --weekdays mon,thu --time 02:30 octocat /backup/github --token ghp_xxx
```
- **Every day at 23:00:**
```bash
python scheduler.py --weekdays mon,tue,wed,thu,fri,sat,sun --time 23:00 myusername
```
The scheduler runs indefinitely until interrupted with Ctrl+C.
# Alternative Automation (cron / systemd)
If you prefer not to keep the scheduler running continuously, you can use the system’s own scheduler (cron, systemd timers, Task Scheduler) to invoke backup_github.py directly.

Example cron job (runs daily at 3am):
```bash
0 3 * * * cd /path/to/script && /usr/bin/python backup_github.py octocat /backup/github --token ghp_xxx
```

# License
This project is licensed under the MIT License.

**Contributions, issues, and feature requests are welcome!**
Feel free to open an issue or submit a pull request.