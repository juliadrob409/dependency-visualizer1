"""Тесты построения графа зависимостей."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.graph import (
    build_maven_graph,
    build_test_graph,
    load_test_graph,
)


class GraphTests(unittest.TestCase):
    """Проверяет построение тестового и Maven-графа."""

    def setUp(self):
        """Создаёт временную папку для тестового графа."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "repository.txt"

    def tearDown(self):
        """Удаляет временные файлы."""
        self.temp_dir.cleanup()

    def write_graph(self, content):
        """Записывает тестовый граф в файл."""
        self.path.write_text(content, encoding="utf-8")

    def test_load_graph(self):
        """Проверяет загрузку графа."""
        self.write_graph("A: B, C\nB: D\nC: D\nD:\n")

        graph = load_test_graph(self.path)

        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["D"], [])

    def test_missing_file(self):
        """Проверяет отсутствие файла графа."""
        with self.assertRaisesRegex(ValueError, "прочитать"):
            load_test_graph(self.path)

    def test_invalid_line(self):
        """Проверяет некорректную строку графа."""
        self.write_graph("A B C\n")

        with self.assertRaisesRegex(ValueError, "строка"):
            load_test_graph(self.path)

    def test_invalid_package_name(self):
        """Проверяет недопустимое имя пакета."""
        self.write_graph("A: abc\n")

        with self.assertRaisesRegex(ValueError, "имя"):
            load_test_graph(self.path)

    def test_missing_start_package(self):
        """Проверяет отсутствие начального пакета."""
        self.write_graph("A: B\nB:\n")

        with self.assertRaisesRegex(ValueError, "Начальный"):
            build_test_graph("C", self.path)

    def test_shared_dependency(self):
        """Проверяет общую зависимость двух пакетов."""
        self.write_graph("A: B, C\nB: D\nC: D\nD:\n")

        graph = build_test_graph("A", self.path)

        self.assertEqual(set(graph), {"A", "B", "C", "D"})
        self.assertEqual(graph["D"], [])

    def test_cycle(self):
        """Проверяет обработку циклических зависимостей."""
        self.write_graph("A: B\nB: C\nC: A\n")

        graph = build_test_graph("A", self.path)

        self.assertEqual(set(graph), {"A", "B", "C"})

    @patch("src.graph.get_direct_dependencies")
    def test_maven_cycle(self, get_dependencies):
        """Проверяет цикл в Maven-графе."""
        root = "org.example:app"
        get_dependencies.side_effect = [
            [{"group_id": "org.example", "artifact_id": "lib",
              "version": "1.0"}],
            [{"group_id": "org.example", "artifact_id": "app",
              "version": "1.0"}],
        ]

        graph = build_maven_graph(root, "1.0", "https://example.com")

        self.assertEqual(len(graph), 2)
        self.assertEqual(get_dependencies.call_count, 2)


if __name__ == "__main__":
    unittest.main()