
"""Точка входа в приложение."""

import sys
from src.config import load_config
from src.graph import (
    build_test_graph,
    build_maven_graph,
    get_load_order,
)


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
    arguments = sys.argv[1:]
    show_order = "--order" in arguments
    arguments = [arg for arg in arguments if arg != "--order"]

    if len(arguments) > 1:
        print("Ошибка: указано слишком много аргументов")
        return 1

    config_path = arguments[0] if arguments else "config.xml"
    try:
        config = load_config(config_path)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    print_config(config)
    try:
        graph = get_graph(config)

        if show_order:
            order = get_load_order(graph)

    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1

    if show_order:
        print("\nПорядок загрузки зависимостей:")

        for package in order:
            print(f"- {package}")
    else:
        print_graph(graph)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
