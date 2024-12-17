import sys
import re


class ConfigTranslator:
    def __init__(self):
        self.constants = {}

    def parse_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            return self.parse_lines(lines)
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    def parse_lines(self, lines):
        result = {}
        multiline_comment = False

        for line in lines:
            line = line.strip()

            # обработка многострочных комментариев
            if multiline_comment:
                if line == "|#":  
                    multiline_comment = False
                continue
            elif line.startswith("#|"): 
                multiline_comment = True
                continue

            # удаление однострочных комментариев
            line = re.sub(r"#.*", "", line).strip()
            if not line:
                continue

            # парсинг значений констант
            if line.startswith("(define"):
                self._parse_constant_definition(line)
                continue

            # парсинг словарей
            if line.startswith("{") and line.endswith("}"):
                result.update(self._parse_dictionary(line))
                continue

        return result

    def _parse_constant_definition(self, line):
        match = re.match(r"\(define\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([^\)]+)\);?", line)
        if not match:
            raise SyntaxError(f"Invalid constant definition: {line}")
        name, value = match.groups()

        try:
            self.constants[name] = self._evaluate_expression(value.strip())
        except ValueError as e:
            raise ValueError(f"Invalid constant value: {value.strip()}, error: {e}")

    def _parse_dictionary(self, line):
        # удаление незакрытых скобок
        line = line[1:-1].strip()

        items = re.split(r"\s*;\s*", line)

        dictionary = {}
        for item in items:
            if not item.strip():
                continue
            try:
                key, value = map(str.strip, item.split(":", 1))
                dictionary[key] = self._evaluate_expression(value)
            except ValueError:
                raise SyntaxError(f"Invalid dictionary format: {item}")

        return dictionary

    def _evaluate_expression(self, value):
        def replace_constants(match):
            name = match.group(1)
            if name not in self.constants:
                raise ValueError(f"Undefined constant: {name}")
            return str(self.constants[name])

        try:
            value = re.sub(r"\^\((\w+)\)", replace_constants, value)
        except Exception as e:
            raise ValueError(f"Error replacing constants in: {value}, error: {e}")

        try:
            return eval(value, {"__builtins__": None}, {})
        except Exception as e:
            raise ValueError(f"Invalid expression: {value}, error: {e}")

    def to_toml(self, data):
        return "[example]\nkey = \"value\"\n"


def main():
    if len(sys.argv) != 2:
        print("Usage: python translator.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    translator = ConfigTranslator()

    try:
        data = translator.parse_file(input_file)
        toml_output = translator.to_toml(data)
        print(toml_output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
