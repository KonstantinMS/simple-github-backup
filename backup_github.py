#!/usr/bin/env python3
"""
Скрипт для бэкапа репозиториев GitHub пользователя или организации.

Использование:
    python backup_github.py USERNAME [BACKUP_DIR] [--token TOKEN]

Если BACKUP_DIR не указан, используется './github_backup_YYYY-MM-DD' (сегодняшняя дата).
Токен можно передать через аргумент --token или через переменную окружения GITHUB_TOKEN.
"""

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com"


def get_repos(username, token=None):
    """Получить список всех репозиториев пользователя через API GitHub."""
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    repos = []
    page = 1
    per_page = 100

    while True:
        url = f"{GITHUB_API}/users/{username}/repos"
        params = {"page": page, "per_page": per_page, "type": "all"}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 404:
            # Возможно, это организация
            url = f"{GITHUB_API}/orgs/{username}/repos"
            response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code} - {response.text}")
            sys.exit(1)

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


def backup_repo(repo_url, dest_path):
    """Клонировать или обновить репозиторий (зеркально)."""
    if dest_path.exists():
        print(f"Обновление {repo_url} в {dest_path}")
        try:
            subprocess.run(
                ["git", "--git-dir", str(dest_path), "remote", "update"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при обновлении {repo_url}: {e.stderr.decode()}")
    else:
        print(f"Клонирование {repo_url} в {dest_path}")
        try:
            subprocess.run(
                ["git", "clone", "--mirror", repo_url, str(dest_path)],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при клонировании {repo_url}: {e.stderr.decode()}")


def main():
    parser = argparse.ArgumentParser(description="Бэкап репозиториев GitHub")
    parser.add_argument("username", help="Имя пользователя или организации GitHub")
    parser.add_argument(
        "backup_dir", nargs="?", help="Папка для сохранения бэкапов (опционально)"
    )
    parser.add_argument(
        "--token", help="Токен GitHub для доступа к приватным репозиториям"
    )
    args = parser.parse_args()

    # Определяем токен: сначала аргумент, потом переменная окружения
    token = args.token or os.environ.get("GITHUB_TOKEN")

    # Определяем корневую папку для бэкапа
    if args.backup_dir:
        backup_root = Path(args.backup_dir)
    else:
        today = date.today().isoformat()
        backup_root = Path(f"./github_backup_{today}")

    backup_root.mkdir(parents=True, exist_ok=True)

    print(f"Получение списка репозиториев для {args.username}...")
    if not token:
        print(
            "Предупреждение: токен не указан. Приватные репозитории не будут доступны."
        )
        repos = get_repos(args.username)
    else:
        repos = get_repos(args.username, token)

    print(f"Найдено репозиториев: {len(repos)}")

    for repo in repos:
        name = repo["name"]
        clone_url = repo["clone_url"]
        dest = backup_root / f"{name}.git"
        backup_repo(clone_url, dest)

    print(f"Готово! Все репозитории сохранены в {backup_root}")


if __name__ == "__main__":
    main()
