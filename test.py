import unittest
import os
from hw3_toml import ConfigLangParser


class TestConfigLangParser(unittest.TestCase):

    def setUp(self):
        """Создание временных файлов для тестирования."""
        self.test_file = "test_input.txt"
        self.invalid_file = "invalid_input.txt"

    def tearDown(self):
        """Удаление временных файлов после тестирования."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.invalid_file):
            os.remove(self.invalid_file)

    def write_file(self, content, file_name=None):
        """Создает тестовый файл с указанным содержимым."""
        if not file_name:
            file_name = self.test_file
        with open(file_name, "w") as f:
            f.write(content)

    def test_simple_constants(self):
        """Тест на корректное преобразование простых констант."""
        content = "const1 = 10\nconst2 = ^{const1 + 5}\n"
        self.write_file(content)

        parser = ConfigLangParser(self.test_file)
        result = parser.parse()

        expected_output = "const1 = 10;\nconst2 = 15;"
        self.assertEqual(result.strip(), expected_output)

    def test_arrays(self):
        """Тест на корректное преобразование массивов."""
        content = "array1 = [4, 5, 6]\narray2 = ^{len(array1)}\n"
        self.write_file(content)

        parser = ConfigLangParser(self.test_file)
        result = parser.parse()

        expected_output = "array1 = #(4, 5, 6);\narray2 = 3;"
        self.assertEqual(result.strip(), expected_output)

    def test_nested_arrays(self):
        """Тест на корректное преобразование вложенных массивов."""
        content = "array3 = [4, 2, [5, 6, 7]]\n"
        self.write_file(content)

        parser = ConfigLangParser(self.test_file)
        result = parser.parse()

        expected_output = "array3 = #(4, 2, #(5, 6, 7));"
        self.assertEqual(result.strip(), expected_output)

    def test_invalid_syntax(self):
        """Тест на некорректный синтаксис TOML."""
        content = "invalid = ^{const1 + }\n"
        self.write_file(content, file_name=self.invalid_file)

        with self.assertRaises(ValueError):
            parser = ConfigLangParser(self.invalid_file)
            parser.parse()

    def test_invalid_name(self):
        """Тест на некорректные имена."""
        content = "123name = 10\n"
        self.write_file(content, file_name=self.invalid_file)

        with self.assertRaises(ValueError):
            parser = ConfigLangParser(self.invalid_file)
            parser.parse()

    def test_mod_function(self):
        """Тест на использование функции mod()."""
        content = "const1 = 10\nconst2 = ^{const1 mod 3}\n"
        self.write_file(content)

        parser = ConfigLangParser(self.test_file)
        result = parser.parse()

        expected_output = "const1 = 10;\nconst2 = 1;"
        self.assertEqual(result.strip(), expected_output)

    def test_len_function(self):
        """Тест на использование функции len()."""
        content = "array1 = [4, 5, 6]\nconst1 = ^{len(array1)}\n"
        self.write_file(content)

        parser = ConfigLangParser(self.test_file)
        result = parser.parse()

        expected_output = "array1 = #(4, 5, 6);\nconst1 = 3;"
        self.assertEqual(result.strip(), expected_output)


if __name__ == "__main__":
    unittest.main()
