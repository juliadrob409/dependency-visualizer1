
"""Точка входа в приложение."""

import sys
from src.config import load_config
from src.graph import build_test_graph, build_maven_graph


MIN_ARGUMENT_COUNT = 2
DISPLAY_NAMES = {
    "package": "Имя пакета",
    "repository": "Репозиторий",
    "test_mode": "Тестовый режим",
    "version": "Версия",
}


def print_config(config):
    """Выводит параметры конфигурации."""
    print("Параметры конфигурации:")

    for key, value in config.items():
        print(f"{DISPLAY_NAMES[key]}: {value}")


def get_graph(config):
    """Строит граф зависимостей."""
    if config["test_mode"]:
        return build_test_graph(
            config["package"],
            config["repository"],
        )

    return build_maven_graph(
        config["package"],
        config["version"],
        config["repository"],
    )


def print_graph(graph):
    """Выводит граф зависимостей."""
    print("\nГраф зависимостей:")

    for package, dependencies in graph.items():
        print(f"{package}:")

        if not dependencies:
            print("  Зависимости отсутствуют.")
            continue

        for dependency in dependencies:
            print(f"  - {dependency}")


def main():
    """Загружает настройки и строит граф зависимостей."""
    config_path = (
        sys.argv[1]
        if len(sys.argv) >= MIN_ARGUMENT_COUNT
        else "config.xml"
    )

    try:
        config = load_config(config_path)
        print_config(config)
        graph = get_graph(config)
        print_graph(graph)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
