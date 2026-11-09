"""Тесты загрузки и проверки XML-конфигурации."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <package>junit:junit</package>
    <repository>https://repo.maven.apache.org/maven2</repository>
    <test_mode>false</test_mode>
    <version>4.13.2</version>
</configuration>
"""


class ConfigTests(unittest.TestCase):
    """Проверяет корректные и ошибочные варианты конфигурации."""

    def setUp(self):
        """Создаёт временную папку для тестовых файлов."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.config_path = self.directory / "config.xml"

    def tearDown(self):
        """Удаляет временные файлы после теста."""
        self.temp_dir.cleanup()

    def write_config(self, content):
        """Записывает XML в тестовый файл."""
        self.config_path.write_text(content, encoding="utf-8")

    def test_valid_configuration(self):
        """Проверяет загрузку корректной конфигурации."""
        self.write_config(VALID_XML)

        config = load_config(self.config_path)

        self.assertEqual(config["package"], "junit:junit")
        self.assertEqual(config["version"], "4.13.2")
        self.assertFalse(config["test_mode"])

    def test_missing_configuration_file(self):
        """Проверяет ошибку при отсутствии XML-файла."""
        with self.assertRaisesRegex(ValueError, "не найден"):
            load_config(self.config_path)

    def test_invalid_xml(self):
        """Проверяет обработку синтаксически неверного XML."""
        self.write_config("<configuration>")

        with self.assertRaisesRegex(ValueError, "формата XML"):
            load_config(self.config_path)

    def test_invalid_root(self):
        """Проверяет имя корневого XML-элемента."""
        self.write_config("<config />")

        with self.assertRaisesRegex(ValueError, "корневой"):
            load_config(self.config_path)

    def test_missing_each_parameter(self):
        """Проверяет отсутствие каждого обязательного параметра."""
        parameters = ("package", "repository", "test_mode", "version")

        for parameter in parameters:
            with self.subTest(parameter=parameter):
                content = VALID_XML.replace(
                    f"<{parameter}>{self._value(parameter)}</{parameter}>",
                    "",
                )
                self.write_config(content)

                with self.assertRaisesRegex(ValueError, "Не указан"):
                    load_config(self.config_path)

    def _value(self, parameter):
        """Возвращает исходное значение параметра тестовой конфигурации."""
        values = {
            "package": "junit:junit",
            "repository": "https://repo.maven.apache.org/maven2",
            "test_mode": "false",
            "version": "4.13.2",
        }
        return values[parameter]

    def test_invalid_package(self):
        """Проверяет формат координат Maven."""
        self.write_config(VALID_XML.replace("junit:junit", "junit"))

        with self.assertRaisesRegex(ValueError, "пакета"):
            load_config(self.config_path)

    def test_invalid_repository_url(self):
        """Проверяет URL реального репозитория."""
        content = VALID_XML.replace(
            "https://repo.maven.apache.org/maven2",
            "ftp://example.com/repository",
        )
        self.write_config(content)

        with self.assertRaisesRegex(ValueError, "URL"):
            load_config(self.config_path)

    def test_invalid_test_mode(self):
        """Проверяет допустимые значения режима работы."""
        self.write_config(VALID_XML.replace("<test_mode>false</test_mode>",
                                            "<test_mode>yes</test_mode>"))

        with self.assertRaisesRegex(ValueError, "test_mode"):
            load_config(self.config_path)

    def test_invalid_version(self):
        """Проверяет формат версии пакета."""
        self.write_config(VALID_XML.replace("4.13.2", "bad version"))

        with self.assertRaisesRegex(ValueError, "версия"):
            load_config(self.config_path)

    def test_test_repository_file(self):
        """Проверяет путь к существующему тестовому файлу."""
        repository_path = self.directory / "repository.txt"
        repository_path.write_text("A: B\nB:\n", encoding="utf-8")
        content = VALID_XML.replace(
            "https://repo.maven.apache.org/maven2",
            "repository.txt",
        ).replace("<test_mode>false</test_mode>",
                  "<test_mode>true</test_mode>")
        self.write_config(content)

        config = load_config(self.config_path)

        self.assertTrue(config["test_mode"])
        self.assertEqual(
            Path(config["repository"]).resolve(),
            repository_path.resolve(),
        )

    def test_missing_test_repository_file(self):
        """Проверяет ошибку при отсутствии тестового файла."""
        content = VALID_XML.replace(
            "https://repo.maven.apache.org/maven2",
            "missing.txt",
        ).replace("<test_mode>false</test_mode>",
                  "<test_mode>true</test_mode>")
        self.write_config(content)

        with self.assertRaisesRegex(ValueError, "не найден"):
            load_config(self.config_path)


if __name__ == "__main__":
    unittest.main()
