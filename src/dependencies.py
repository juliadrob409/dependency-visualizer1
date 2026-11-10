"""Получение прямых зависимостей Maven-пакета."""

from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import xml.etree.ElementTree as element_tree


TIMEOUT = 10


def build_pom_url(package, version, repository):
    """Формирует URL POM-файла Maven."""
    group_id, artifact_id = package.split(":")
    group_path = group_id.replace(".", "/")
    file_name = f"{artifact_id}-{version}.pom"

    return (
        f"{repository}/{group_path}/{artifact_id}/"
        f"{version}/{file_name}"
    )


def download_pom(url):
    """Скачивает POM-файл по указанному URL."""
    try:
        with urlopen(url, timeout=TIMEOUT) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError) as error:
        raise ValueError(
            f"Не удалось получить POM-файл: {error}"
        ) from error


def _find_child(element, name):
    """Находит дочерний элемент XML по имени."""
    for child in element:
        if child.tag.split("}")[-1] == name:
            return child

    return None


def _get_text(element, name):
    """Возвращает текст дочернего XML-элемента."""
    child = _find_child(element, name)

    if child is None or child.text is None:
        return ""

    return child.text.strip()


def _get_properties(root):
    """Получает свойства Maven из POM-файла."""
    properties_element = _find_child(root, "properties")
    properties = {}

    if properties_element is None:
        return properties

    for element in properties_element:
        name = element.tag.split("}")[-1]
        value = element.text.strip() if element.text else ""
        properties[name] = value

    return properties


def _resolve_version(version, properties):
    """Подставляет значение свойства Maven в версию."""
    if version.startswith("${") and version.endswith("}"):
        property_name = version[2:-1]
        return properties.get(property_name, version)

    return version

def _parse_dependency(element, properties):
    """Извлекает данные одной зависимости."""
    dependency = {
        "group_id": _get_text(element, "groupId"),
        "artifact_id": _get_text(element, "artifactId"),
        "version": _resolve_version(
            _get_text(element, "version"),
            properties,
        ),
        "scope": _get_text(element, "scope") or "compile",
    }

    if not dependency["group_id"] or not dependency["artifact_id"]:
        raise ValueError(
            "В зависимости отсутствует groupId или artifactId"
        )

    return dependency

def parse_pom(content):
    """Извлекает прямые зависимости из POM-файла."""
    try:
        root = element_tree.fromstring(content)
    except element_tree.ParseError as error:
        raise ValueError(
            "Некорректный формат POM-файла"
        ) from error

    properties = _get_properties(root)
    dependencies_element = _find_child(root, "dependencies")

    if dependencies_element is None:
        return []

    dependencies = []

    for element in dependencies_element:
        if element.tag.split("}")[-1] == "dependency":
            dependencies.append(
                _parse_dependency(element, properties)
            )

    return dependencies


def get_direct_dependencies(package, version, repository):
    """Получает прямые зависимости Maven-пакета."""
    url = build_pom_url(package, version, repository)
    content = download_pom(url)

    return parse_pom(content)