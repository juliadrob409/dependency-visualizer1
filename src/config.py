
"""Загрузка и проверка конфигурации приложения."""

import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


PACKAGE_PART_COUNT = 2
VALID_MODES = {"true", "false"}


def is_valid_package_part(value):
    """Проверяет допустимые символы в названии пакета."""
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789_.-"
    )
    return bool(value) and all(char in allowed for char in value)


def is_valid_version(value):
    """Проверяет допустимые символы в версии пакета."""
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789._+-"
    )
    return bool(value) and value[0].isalnum() and all(
        char in allowed for char in value
    )


def _read_parameter(root, name):
    """Возвращает непустое значение XML-параметра."""
    element = root.find(name)

    if element is None or element.text is None:
        raise ValueError(f"Не указан параметр: {name}")

    value = element.text.strip()

    if not value:
        raise ValueError(f"Не указан параметр: {name}")

    return value


def _validate_package(package, test_mode):
    """Проверяет имя пакета."""
    if test_mode and is_test_package(package):
        return

    parts = package.split(":")

    if len(parts) != 2 or not all(parts):
        raise ValueError("Некорректное имя пакета")

    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    )

    for part in parts:
        if not all(char in allowed for char in part):
            raise ValueError("Некорректное имя Maven-пакета")


def is_test_package(package):
    """Проверяет имя тестового пакета."""
    return bool(package) and all(
        "A" <= char <= "Z" for char in package
    )


def _validate_repository(repository, test_mode, config_dir):
    """Проверяет URL репозитория или путь к тестовому файлу."""
    if test_mode:
        repository_path = Path(repository)

        if not repository_path.is_absolute():
            repository_path = config_dir / repository_path

        if not repository_path.is_file():
            raise ValueError("Файл тестового репозитория не найден")

        return str(repository_path.resolve())

    parsed_url = urlparse(repository)

    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("Некорректный URL репозитория")

    return repository.rstrip("/")


def load_config(path="config.xml"):
    """Загружает XML и возвращает проверенные параметры приложения."""
    config_path = Path(path).resolve()
    try:
        root = ET.parse(config_path).getroot()
    except FileNotFoundError as error:
        raise ValueError("Файл конфигурации не найден") from error
    except ET.ParseError as error:
        raise ValueError("Ошибка формата XML") from error

    if root.tag != "configuration":
        raise ValueError("Неверный корневой элемент XML")

    package = _read_parameter(root, "package")
    repository = _read_parameter(root, "repository")
    mode_value = _read_parameter(root, "test_mode").lower()
    version = _read_parameter(root, "version")

    if mode_value not in VALID_MODES:
        raise ValueError("test_mode должен быть true или false")


    if not is_valid_version(version):
        raise ValueError("Некорректная версия пакета")

    test_mode = mode_value == "true"
    repository = _validate_repository(
        repository,
        test_mode,
        config_path.parent,
    )
    _validate_package(package, test_mode)

    return {
        "package": package,
        "repository": repository,
        "test_mode": test_mode,
        "version": version,
    }
