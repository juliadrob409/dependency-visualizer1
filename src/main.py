"""Точка входа в приложение."""

import sys

from src.config import load_config

MIN_ARGUMENT_COUNT = 2

DISPLAY_NAMES = {
    "package": "Имя пакета",
    "repository": "Репозиторий",
    "test_mode": "Тестовый режим",
    "version": "Версия",
}


def main():
    """Загружает настройки и выводит их в формате ключ-значение."""
    config_path = (
        sys.argv[1]
        if len(sys.argv) >= MIN_ARGUMENT_COUNT
        else "config.xml"
    )

    try:
        config = load_config(config_path)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    print("Параметры конфигурации:")

    for key, value in config.items():
        print(f"{DISPLAY_NAMES[key]}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
