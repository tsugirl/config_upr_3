import unittest
from io import StringIO
from translator import ConfigTranslator

class TestConfigTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = ConfigTranslator()

    def test_parse_constant_definition(self):
        # проверка корректного определения константы
        self.translator._parse_constant_definition("(define CONST1 100);")
        self.assertEqual(self.translator.constants["CONST1"], 100)

        # проверка некорректного определения константы
        with self.assertRaises(SyntaxError):
            self.translator._parse_constant_definition("(define CONST1);")

    def test_evaluate_expression_with_constants(self):
        self.translator.constants = {"CONST1": 100, "CONST2": 200}

        # проверка использования констант
        result = self.translator._evaluate_expression("^(CONST1) + ^(CONST2)")
        self.assertEqual(result, 300)

        # проверка использования неопределённой константы
        with self.assertRaises(ValueError):
            self.translator._evaluate_expression("^(CONST3)")

    def test_parse_dictionary(self):
        self.translator.constants = {"CONST1": 100, "CONST2": 200}

        # проверка словника
        dictionary = self.translator._parse_dictionary("{ key1 : ^(CONST1); key2 : ^(CONST2); }")
        self.assertEqual(dictionary, {"key1": 100, "key2": 200})

    def test_parse_lines(self):
        lines = [
            "#|", 
            "Многострочный комментарий", 
            "|#", 
            "(define CONST1 100);", 
            "(define CONST2 200);", 
            "{ key1 : ^(CONST1); key2 : ^(CONST2); }"
        ]

        result = self.translator.parse_lines(lines)
        self.assertEqual(result, {"key1": 100, "key2": 200})

    def test_parse_file(self):
        # симуляция файла
        file_content = """#|
        Многострочный комментарий
        |#
        (define CONST1 100);
        (define CONST2 200);
        { key1 : ^(CONST1); key2 : ^(CONST2); }
        """
        with open("test_input.txt", "w", encoding="utf-8") as f:
            f.write(file_content)

        result = self.translator.parse_file("test_input.txt")
        self.assertEqual(result, {"key1": 100, "key2": 200})

    def test_to_toml(self):
        data = {"key1": 100, "key2": {"nested_key": 200}}
        toml_result = self.translator.to_toml(data)
        expected_toml = """key1 = 100

[key2]
nested_key = 200
"""
        self.assertEqual(toml_result.strip(), expected_toml.strip())

if __name__ == "__main__":
    unittest.main()
