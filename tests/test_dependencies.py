"""Тесты получения прямых зависимостей Maven."""

import unittest
from unittest.mock import MagicMock, patch

from src.dependencies import (
    build_pom_url,
    download_pom,
    get_direct_dependencies,
    parse_pom,
)


POM_CONTENT = b"""<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <dependencies>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
            <version>1.3</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>3.12.4</version>
        </dependency>
    </dependencies>
</project>
"""


class DependencyTests(unittest.TestCase):
    """Проверяет функции работы с Maven-зависимостями."""

    def test_build_pom_url(self):
        url = build_pom_url(
            "junit:junit",
            "4.13.2",
            "https://repo.maven.apache.org/maven2",
        )

        self.assertEqual(
            url,
            "https://repo.maven.apache.org/maven2/"
            "junit/junit/4.13.2/junit-4.13.2.pom",
        )

    def test_parse_pom(self):
        dependencies = parse_pom(POM_CONTENT)

        self.assertEqual(len(dependencies), 2)
        self.assertEqual(
            dependencies[0]["group_id"],
            "org.hamcrest",
        )
        self.assertEqual(
            dependencies[0]["scope"],
            "test",
        )

    def test_parse_pom_without_dependencies(self):
        content = b"<project></project>"

        self.assertEqual(parse_pom(content), [])

    def test_parse_invalid_pom(self):
        with self.assertRaises(ValueError):
            parse_pom(b"<project>")

    def test_download_pom(self):
        response = MagicMock()
        response.read.return_value = POM_CONTENT

        with patch(
            "src.dependencies.urlopen"
        ) as mocked_urlopen:
            mocked_urlopen.return_value.__enter__.return_value = (
                response
            )
            result = download_pom("https://example.com/test.pom")

        self.assertEqual(result, POM_CONTENT)

    @patch("src.dependencies.download_pom")
    def test_get_direct_dependencies(self, mocked_download):
        mocked_download.return_value = POM_CONTENT

        dependencies = get_direct_dependencies(
            "junit:junit",
            "4.13.2",
            "https://repo.maven.apache.org/maven2",
        )

        self.assertEqual(len(dependencies), 2)
        mocked_download.assert_called_once()

    def test_missing_dependency_fields(self):
        content = b"""
        <project>
            <dependencies>
                <dependency>
                    <version>1.0</version>
                </dependency>
            </dependencies>
        </project>
        """

        with self.assertRaises(ValueError):
            parse_pom(content)


if __name__ == "__main__":
    unittest.main()