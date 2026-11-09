"""Точка входа в приложение."""
import sys
from src.config import load_config
from src.dependencies import get_direct_dependencies
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

def main():
    """Загружает настройки и выводит их в формате ключ-значение."""
    config_path = (
        sys.argv[1]
        if len(sys.argv) >= MIN_ARGUMENT_COUNT
        else "config.xml")
    try:
        config = load_config(config_path)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1
    print_config(config)
    if config["test_mode"]:
        print("Ошибка: для второго этапа установите test_mode=false")
        return 1
    try:
        dependencies = get_direct_dependencies(
            config["package"],
            config["version"],
            config["repository"],)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return 1
    print("\nПрямые зависимости:")
    if not dependencies:
        print("Зависимости не найдены.")
    else:
        for dependency in dependencies:
            package = (
                f"{dependency['group_id']}:"
                f"{dependency['artifact_id']}"
            )
            version = dependency["version"] or "не указана"
            scope = dependency["scope"]

            print(
                f"- {package}, версия: {version}, "
                f"scope: {scope}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
