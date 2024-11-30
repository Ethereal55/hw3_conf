import argparse
import re
import sys


class ConfigLangParser:
    def __init__(self, txt_file):
        self.constants = {}
        self.data = self.load_custom_toml(txt_file)

    def load_custom_toml(self, file_path):
        """Парсит файл с поддержкой выражений вида ^{...}."""
        data = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):  # Пропускаем пустые строки и комментарии
                        continue
                    key, value = map(str.strip, line.split("=", 1))
                    if value.startswith("[") and value.endswith("]"):  # Массив
                        data[key] = eval(value)  # Преобразуем массив в Python-объект
                    elif value.startswith("^{") and value.endswith("}"):  # Константное выражение
                        data[key] = value
                    else:
                        try:
                            data[key] = int(value)  # Простое число
                        except ValueError:
                            raise ValueError(f"Некорректное значение: {value}")
            return data
        except FileNotFoundError:
            print(f"Файл не найден: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Ошибка обработки файла: {e}")
            sys.exit(1)

    def validate_name(self, name):
        """Проверяет корректность имени."""
        if not re.match(r"^[a-zA-Z][_a-zA-Z0-9]*$", name):
            raise ValueError(f"Некорректное имя: {name}")

    def evaluate_expression(self, expression):
        """Вычисляет константное выражение."""
        expression = expression.strip()[2:-1]  # Убираем ^{ и }
        try:
            # Замена имён констант на их значения
            for name, value in self.constants.items():
                expression = expression.replace(name, str(value))

            # Поддержка функций mod() и len()
            expression = expression.replace("mod", "%")
            expression = re.sub(r"len\((.*?)\)", lambda m: str(len(eval(m.group(1)))), expression)

            return eval(expression)
        except Exception as e:
            raise ValueError(f"Ошибка вычисления выражения: {expression}, {e}")

    def format_array(self, array):
        """Рекурсивно форматирует массив в целевой синтаксис."""
        formatted = []
        for item in array:
            if isinstance(item, list):  # Вложенный массив
                formatted.append(self.format_array(item))
            else:
                formatted.append(str(item))
        return f"#({', '.join(formatted)})"

    def transform_to_custom_format(self):
        """Трансформирует данные в целевой формат."""
        output_lines = []
        for key, value in self.constants.items():
            if isinstance(value, list):
                formatted_value = self.format_array(value)
            elif isinstance(value, int):
                formatted_value = str(value)
            else:
                raise ValueError(f"Неподдерживаемый тип данных для {key}: {type(value)}")
            output_lines.append(f"{key} = {formatted_value};")
        return "\n".join(output_lines)

    def parse(self):
        """Основной метод обработки."""
        for key, value in self.data.items():
            self.validate_name(key)
            if isinstance(value, str) and value.startswith("^{"):
                self.constants[key] = self.evaluate_expression(value)
            else:
                self.constants[key] = value

        return self.transform_to_custom_format()


def main():
    parser = argparse.ArgumentParser(description="Инструмент преобразования TOML в учебный конфигурационный язык.")
    parser.add_argument("input_file", help="Путь к входному .txt-файлу с текстом TOML.")
    args = parser.parse_args()

    try:
        config_parser = ConfigLangParser(args.input_file)
        output = config_parser.parse()
        print(output)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
