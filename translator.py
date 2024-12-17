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
                if line.endswith("#"):
                    multiline_comment = False
                continue
            elif line.startswith("# |"):
                if not line.endswith("| #"):
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
        print(f"Defining constant from line: {line.strip()}")
        match = re.match(r"\(define\s+([a-zA-Z]+)\s+([^\)]+)\)", line)
        if not match:
            raise SyntaxError(f"Invalid constant definition: {line}")
        name, value = match.groups()
        if re.match(r"^\d+$", value):
            value = int(value)
        else:
            raise SyntaxError(f"Invalid constant value: {value}")
        self.constants[name] = value

    def _parse_dictionary(self, line):
        print(f"Parsing dictionary: {line.strip()}")
        line = line[1:-1].strip()  # удаление символов "{" и "}" при обработке словарей
        items = line.split(";")
        dictionary = {}

        for item in items:
            if not item.strip():
                continue
            key, value = map(str.strip, item.split(":", 1))
            if re.match(r"^\d+$", value):
                value = int(value)
            else:
                raise SyntaxError(f"Invalid dictionary value: {value}")
            dictionary[key] = value

        return dictionary

    def to_toml(self, data):
        print("Converting to TOML...")
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
