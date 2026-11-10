"""Построение графа зависимостей."""

from src.dependencies import get_direct_dependencies
UNVISITED = 0
VISITING = 1
VISITED = 2

def is_valid_name(name):
    """Проверяет имя тестового пакета."""
    return bool(name) and all("A" <= char <= "Z" for char in name)


def _read_test_lines(path):
    """Читает строки тестового файла."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()
    except OSError as error:
        raise ValueError(
            "Не удалось прочитать файл графа"
        ) from error


def _parse_test_line(line, graph):
    """Проверяет и разбирает строку тестового графа."""
    if not line.strip():
        return None

    if line.count(":") != 1:
        raise ValueError("Некорректная строка тестового графа")

    package, dependencies = line.strip().split(":")
    package = package.strip()
    names = dependencies.replace(",", " ").split()

    if not is_valid_name(package) or package in graph:
        raise ValueError("Некорректное имя пакета")

    if not all(is_valid_name(name) for name in names):
        raise ValueError("Некорректное имя зависимости")

    return package, names


def _add_missing_packages(graph):
    """Добавляет в граф пакеты без зависимостей."""
    all_dependencies = {
        name for names in graph.values() for name in names
    }

    for name in all_dependencies:
        graph.setdefault(name, [])


def load_test_graph(path):
    """Загружает граф из тестового файла."""
    graph = {}

    for line in _read_test_lines(path):
        parsed = _parse_test_line(line, graph)

        if parsed is not None:
            package, names = parsed
            graph[package] = names

    _add_missing_packages(graph)
    return graph


def build_test_graph(start_package, repository):
    """Строит тестовый граф с помощью итеративного DFS."""
    graph = load_test_graph(repository)

    if start_package not in graph:
        raise ValueError("Начальный пакет отсутствует в графе")

    result = {}
    visited = set()
    stack = [start_package]

    while stack:
        package = stack.pop()

        if package in visited:
            continue

        visited.add(package)
        dependencies = graph[package]
        result[package] = dependencies

        for dependency in reversed(dependencies):
            if dependency not in visited:
                stack.append(dependency)

    return result


def _make_node(dependency):
    """Формирует имя узла Maven-графа."""
    package = (
        f"{dependency['group_id']}:{dependency['artifact_id']}"
    )
    version = dependency["version"]

    if not version or "${" in version:
        raise ValueError(f"Не удалось определить версию {package}")

    return f"{package}:{version}"


def build_maven_graph(package, version, repository):
    """Строит Maven-граф с помощью итеративного DFS."""
    start = f"{package}:{version}"
    graph = {}
    visited = set()
    stack = [(package, version)]

    while stack:
        current, current_version = stack.pop()
        node = f"{current}:{current_version}"

        if node in visited:
            continue

        visited.add(node)
        dependencies = get_direct_dependencies(
            current, current_version, repository
        )
        nodes = [_make_node(item) for item in dependencies]
        graph[node] = nodes

        for item in reversed(dependencies):
            dependency = (
                f"{item['group_id']}:{item['artifact_id']}"
            )
            stack.append((dependency, item["version"]))

    return graph

def get_load_order(graph):
    """Определяет порядок загрузки пакетов."""
    states = {}
    order = []

    for start in graph:
        stack = [(start, False)]

        while stack:
            package, expanded = stack.pop()
            state = states.get(package, UNVISITED)

            if expanded:
                states[package] = VISITED
                order.append(package)
                continue

            if state == VISITED:
                continue

            if state == VISITING:
                raise ValueError("Обнаружен цикл зависимостей")

            states[package] = VISITING
            stack.append((package, True))

            for dependency in reversed(graph[package]):
                dep_state = states.get(dependency, UNVISITED)

                if dep_state == VISITING:
                    raise ValueError("Обнаружен цикл зависимостей")

                if dep_state == UNVISITED:
                    stack.append((dependency, False))

    return order