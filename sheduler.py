#!/usr/bin/env python3
"""
Планировщик для автоматического бэкапа репозиториев GitHub.
Поддерживает два режима:
  1. По интервалу (--interval) – запуск каждые N часов.
  2. По дням недели и времени (--weekdays и --time) – запуск в указанные дни в заданное время.

Если не указаны ни интервал, ни дни/время, используется интервал по умолчанию 24 часа.

Примеры:
  # octocat -- имя пользователя
  # Каждые 12 часов
  python scheduler.py --interval 12 octocat --token TOKEN

  # Каждый понедельник, среду и пятницу в 10:30 утра (локальное время)
  python scheduler.py --weekdays mon,wed,fri --time 10:30 octocat --token TOKEN

  # Каждый день в 02:00
  python scheduler.py --weekdays mon,tue,wed,thu,fri,sat,sun --time 02:00 octocat
"""

import argparse
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta

# Константы
DEFAULT_INTERVAL_HOURS = 24
BACKUP_SCRIPT = "backup_github.py"

# Сопоставление названий дней недели с числами (понедельник = 0)
DAY_NAMES = {
    # русские
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
    "вс": 6,
    # английские
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
    # полные английские
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_weekdays(weekdays_str):
    """Преобразует строку с днями (через запятую) в список чисел (0-6)."""
    if not weekdays_str:
        return []
    days = []
    for part in weekdays_str.split(","):
        part = part.strip().lower()
        if part in DAY_NAMES:
            days.append(DAY_NAMES[part])
        else:
            raise ValueError(f"Неизвестный день недели: {part}")
    return sorted(set(days))  # уникальные и отсортированные


def parse_time(time_str):
    """Парсит время в формате ЧЧ:ММ, возвращает (часы, минуты)."""
    match = re.fullmatch(r"([0-9]{1,2}):([0-9]{2})", time_str)
    if not match:
        raise ValueError("Время должно быть в формате ЧЧ:ММ (например 14:30)")
    h, m = map(int, match.groups())
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("Часы должны быть 0-23, минуты 0-59")
    return h, m


def next_weekday_time(now, weekdays, target_hour, target_minute):
    """
    Возвращает ближайший момент времени (datetime) в будущем,
    который соответствует одному из дней weekdays и времени target_hour:target_minute.
    Если такой момент уже сегодня и не прошёл, возвращается сегодня.
    Иначе ищется следующий подходящий день.
    """
    current_weekday = now.weekday()  # понедельник = 0
    current_time = now.time()

    # Целевое время сегодня
    target_today = now.replace(
        hour=target_hour, minute=target_minute, second=0, microsecond=0
    )

    # Если сегодня подходящий день и текущее время <= целевого, то сегодня
    if current_weekday in weekdays and current_time <= target_today.time():
        return target_today

    # Иначе ищем следующий подходящий день
    for days_ahead in range(1, 8):  # максимум неделя
        next_day = now + timedelta(days=days_ahead)
        if next_day.weekday() in weekdays:
            return next_day.replace(
                hour=target_hour, minute=target_minute, second=0, microsecond=0
            )

    # Теоретически сюда не дойдём, если weekdays не пуст
    raise RuntimeError("Не удалось найти следующий день недели")


def run_backup(backup_args):
    """Запускает backup_github.py с переданными аргументами."""
    cmd = [sys.executable, BACKUP_SCRIPT] + backup_args
    print(f"[{datetime.now().isoformat()}] Запуск: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[{datetime.now().isoformat()}] Бэкап успешно завершён")
    except subprocess.CalledProcessError as e:
        print(
            f"[{datetime.now().isoformat()}] Ошибка при выполнении бэкапа (код {e.returncode})"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Планировщик бэкапов GitHub",
        epilog="Примеры использования см. в начале файла.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        help="Интервал между бэкапами в часах (если не указаны --weekdays и --time)",
    )
    parser.add_argument(
        "--weekdays",
        help="Дни недели через запятую: пн,вт,ср,чт,пт,сб,вс или английские",
    )
    parser.add_argument(
        "--time", help="Время запуска в формате ЧЧ:ММ (обязательно вместе с --weekdays)"
    )
    parser.add_argument(
        "other_args",
        nargs=argparse.REMAINDER,
        help="Аргументы для backup_github.py (будут переданы без изменений)",
    )

    args = parser.parse_args()

    if not args.other_args:
        print("Ошибка: не указаны аргументы для backup_github.py (хотя бы username)")
        parser.print_help()
        sys.exit(1)

    # Проверка корректности комбинации аргументов
    using_schedule = args.weekdays is not None or args.time is not None
    if using_schedule:
        if args.weekdays is None or args.time is None:
            print(
                "Ошибка: для расписания по дням недели нужно указать и --weekdays, и --time"
            )
            sys.exit(1)
        try:
            weekdays = parse_weekdays(args.weekdays)
            target_hour, target_minute = parse_time(args.time)
        except ValueError as e:
            print(f"Ошибка в параметрах расписания: {e}")
            sys.exit(1)
        mode = "weekdays"
        interval = None
    else:
        # Режим интервала
        interval = (
            args.interval if args.interval is not None else DEFAULT_INTERVAL_HOURS
        )
        if interval <= 0:
            print("Интервал должен быть положительным числом")
            sys.exit(1)
        mode = "interval"
        weekdays = target_hour = target_minute = None

    print(f"Планировщик запущен. Режим: {mode}")
    if mode == "interval":
        print(f"Интервал: {interval} ч")
    else:
        days_str = ", ".join(
            [k for k, v in DAY_NAMES.items() if v in weekdays][:7]
        )  # краткое представление
        print(
            f"Дни недели: {days_str}, время: {target_hour:02d}:{target_minute:02d} (локальное)"
        )

    print(f"Аргументы для бэкапа: {' '.join(args.other_args)}")

    try:
        while True:
            if mode == "interval":
                # Запускаем сразу при старте, потом ждём интервал
                run_backup(args.other_args)
                print(
                    f"Следующий запуск через {interval} ч (в {time.ctime(time.time() + interval*3600)})"
                )
                time.sleep(interval * 3600)
            else:  # режим weekdays
                now = datetime.now()
                next_run = next_weekday_time(now, weekdays, target_hour, target_minute)
                wait_seconds = (next_run - now).total_seconds()
                if wait_seconds < 0:
                    # Если вдруг next_run в прошлом (защита), пересчитаем
                    next_run = next_weekday_time(
                        now + timedelta(minutes=1), weekdays, target_hour, target_minute
                    )
                    wait_seconds = (next_run - now).total_seconds()

                print(
                    f"Следующий запуск в {next_run.isoformat()} (через {wait_seconds/3600:.2f} ч)"
                )
                time.sleep(wait_seconds)

                # Выполняем бэкап
                run_backup(args.other_args)

    except KeyboardInterrupt:
        print("\nПланировщик остановлен пользователем.")
        sys.exit(0)


if __name__ == "__main__":
    main()
