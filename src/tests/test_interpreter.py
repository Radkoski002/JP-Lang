import io
import pytest

from interpreter.interpreter_class import Interpreter
from lexer.lexer_class import Lexer
from parser.parser_class import Parser
from utils.error_handler_class import ErrorHandler
from interpreter.interpreter_error_classes import *


def functions_template(functions: list[str]):
    functions = "\n".join([f"    {function}" for function in functions])
    return f"""{functions}"""


def funcion_template(name, statements: list[str], arguments=""):
    statements = "\n".join([f"    {statement}" for statement in statements])
    return f"""
    {name}({arguments}) {{
    {statements}
}}"""


def conditional_template(name, condition, body):
    return f"""{name} ({condition}) {{
    {body}
}}"""


def block_template(name, body):
    return f"""{name} {{
    {body}
}}"""


def interpreter_init(body: list[str]):
    error_handler = ErrorHandler()
    final_input = functions_template(body)
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        program = parser.parse()
        interpreter = Interpreter(error_handler)
        interpreter.visit(program)
    return error_handler


def test_init():
    error_handler = interpreter_init([funcion_template("main", [])])
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "input, expected",
    [
        # int operations
        ("1", 1),
        ("-1", -1),
        ("1 + 1", 2),
        ("1 - 1", 0),
        ("1 * 1", 1),
        ("1 / 1", 1.0),
        ("1 % 1", 0),
        ("1 > 1", False),
        ("1 < 1", False),
        ("1 >= 1", True),
        ("1 <= 1", True),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 != 2", True),
        # float operations
        ("1.0", 1.0),
        ("-1.0", -1.0),
        ("1.0 + 1.0", 2.0),
        ("1.0 - 1.0", 0.0),
        ("1.0 * 1.0", 1.0),
        ("1.0 / 1.0", 1.0),
        ("1.0 % 1.0", 0.0),
        ("1.0 > 1.0", False),
        ("1.0 < 1.0", False),
        ("1.0 >= 1.0", True),
        ("1.0 <= 1.0", True),
        ("1.0 == 1.0", True),
        ("1.0 != 1.0", False),
        ("1.0 != 2.0", True),
        # string
        ('"Hello World"', "Hello World"),
        # bool
        ("true", True),
        ("false", False),
        ("true & true", True),
        ("true & false", False),
        ("false & true", False),
        ("false & false", False),
        ("true | true", True),
        ("true | false", True),
        ("false | true", True),
        ("false | false", False),
        ("!true", False),
        ("!false", True),
        # array operations
        ("Array()", []),
        ("Array(1)", [1]),
        ("Array(1, 2)", [1, 2]),
        ("Array(1).get(0)", 1),
        ("Array(1, 2).get(0)", 1),
        ("Array(1, 2).get(1)", 2),
        # property access
        ('Student("Maciej", "Boruwa", 20).name', "Maciej"),
        ('Student("Maciej", "Boruwa", 20).surname', "Boruwa"),
        ('Student("Maciej", "Boruwa", 20).age', "20"),
        ("Student()?.name", "null"),
        ("Student()?.surname", "null"),
        ("Student()?.age", "null"),
        ("Array(1, 2)?.test()", "null"),
        # type checking
        ("1 is Int", True),
        ("1.0 is Float", True),
        ("true is Boolean", True),
        ("false is Boolean", True),
        ('"Hello World" is String', True),
        ("null is Null", True),
        ("Array() is Array", True),
        ("Student() is Student", True),
    ],
)
def test_base_expressions(input, expected, capsys):
    error_handler = interpreter_init([funcion_template("main", [f"print({input});"])])
    out = capsys.readouterr()
    assert out.out == f"{expected}"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "condition",
    [
        "true",
        "1 > 0",
        "1 < 2",
        "1 >= 1",
        "1 <= 1",
        "1 == 1",
        "1 != 2",
        "1.0 > 0.0",
        "1.0 < 2.0",
        "1.0 >= 1.0",
        "1.0 <= 1.0",
        "1.0 == 1.0",
        "1.0 != 2.0",
    ],
)
def test_if_statement(capsys, condition):
    template = funcion_template(
        "main", [conditional_template("if", condition, "print(1);")]
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == "1"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "condition, expected",
    [
        ("true", "1"),
        ("1 > 0", "1"),
        ("1 < 2", "1"),
        ("1 >= 1", "1"),
        ("1 <= 1", "1"),
        ("1 == 1", "1"),
        ("1 != 2", "1"),
        ("1.0 > 0.0", "1"),
        ("1.0 < 2.0", "1"),
        ("1.0 >= 1.0", "1"),
        ("1.0 <= 1.0", "1"),
        ("1.0 == 1.0", "1"),
        ("1.0 != 2.0", "1"),
        ("false", "2"),
        ("1 > 2", "2"),
        ("1 < 0", "2"),
        ("1 >= 2", "2"),
        ("1 <= 0", "2"),
        ("1 == 2", "2"),
        ("1 != 1", "2"),
        ("1.0 > 2.0", "2"),
        ("1.0 < 0.0", "2"),
        ("1.0 >= 2.0", "2"),
        ("1.0 <= 0.0", "2"),
        ("1.0 == 2.0", "2"),
        ("1.0 != 1.0", "2"),
    ],
)
def test_if_else_statement(capsys, condition, expected):
    template = funcion_template(
        "main",
        [
            conditional_template("if", condition, "print(1);"),
            block_template("else", "print(2);"),
        ],
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == f"{expected}"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "if_condition, elif_condition, expected",
    [
        ("true", "false", "1"),
        ("1 > 0", "1 < 0", "1"),
        ("1 < 2", "1 > 2", "1"),
        ("1 >= 1", "1 < 1", "1"),
        ("1 <= 1", "1 > 1", "1"),
        ("1 == 1", "1 != 1", "1"),
        ("1 != 2", "1 == 2", "1"),
        ("1.0 > 0.0", "1.0 < 0.0", "1"),
        ("1.0 < 2.0", "1.0 > 2.0", "1"),
        ("1.0 >= 1.0", "1.0 < 1.0", "1"),
        ("1.0 <= 1.0", "1.0 > 1.0", "1"),
        ("1.0 == 1.0", "1.0 != 1.0", "1"),
        ("1.0 != 2.0", "1.0 == 2.0", "1"),
        ("false", "true", "2"),
        ("1 > 2", "1 < 2", "2"),
        ("1 < 0", "1 > 0", "2"),
        ("1 >= 2", "1 < 2", "2"),
        ("1 <= 0", "1 > 0", "2"),
        ("1 == 2", "1 != 2", "2"),
        ("1 != 1", "1 == 1", "2"),
        ("1.0 > 2.0", "1.0 < 2.0", "2"),
        ("1.0 < 0.0", "1.0 > 0.0", "2"),
        ("1.0 >= 2.0", "1.0 <= 2.0", "2"),
        ("1.0 <= 0.0", "1.0 >= 0.0", "2"),
        ("1.0 == 2.0", "1.0 != 2.0", "2"),
        ("1.0 != 1.0", "1.0 == 1.0", "2"),
        ("false", "false", "3"),
    ],
)
def test_if_elif_else_statement(capsys, if_condition, elif_condition, expected):
    template = funcion_template(
        "main",
        [
            conditional_template("if", if_condition, "print(1);"),
            conditional_template("elif", elif_condition, "print(2);"),
            block_template("else", "print(3);"),
        ],
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == f"{expected}"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "init_value, expression, expected",
    [
        # value change
        ("1", "a = 2", "2"),
        ("1", "a = 2.0", "2.0"),
        ("1", "a = true", "True"),
        ("1", "a = false", "False"),
        ("1", 'a = "Hello"', "Hello"),
        ("1", "a = Array()", "[]"),
        ("1", "a = Array(1)", "[1]"),
        ("1", "a = Array(1, 2)", "[1, 2]"),
        # value change with operations
        ("1", "a += 2", "3"),
        ("1", "a += 2.0", "3.0"),
        ("1", "a -= 2", "-1"),
        ("1", "a -= 2.0", "-1.0"),
        ("1", "a *= 2", "2"),
        ("1", "a *= 2.0", "2.0"),
        ("1", "a /= 2", "0.5"),
        ("1", "a /= 2.0", "0.5"),
        ("1", "a %= 2", "1"),
        ("1", "a %= 2.0", "1.0"),
        # array operations
        ("Array()", "a.add(1)", "[1]"),
        ("Array(1)", "a.add(2)", "[1, 2]"),
        ("Array(3, 2, 1)", "a.remove(1)", "[3, 2]"),
        ("Array(3, 2, 1)", "a.remove(2)", "[3, 1]"),
        ("Array(3, 2, 1)", "a.removeAt(0)", "[2, 1]"),
        ("Array(3, 2, 1)", "a.removeAt(1)", "[3, 1]"),
        ("Array(3, 2, 1)", "a.clear()", "[]"),
        ("Array(3, 2, 1)", "a = a.size()", "3"),
        ("Array(3, 2, 1)", "a = a.get(0)", "3"),
        ("Array(3, 2, 1)", "a = a.get(1)", "2"),
        ("Array(3, 2, 1)", "a.set(0, 1)", "[1, 2, 1]"),
        ("Array(3, 2, 1)", "a.set(1, 3)", "[3, 3, 1]"),
        ("Array(3, 2, 1)", "a = a.contains(1)", "True"),
        ("Array(3, 2, 1)", "a = a.contains(4)", "False"),
        ("Array(3, 2, 1)", "a = a.indexOf(3)", "0"),
        ("Array(3, 2, 1)", "a = a.indexOf(2)", "1"),
    ],
)
def test_variable_change_expressions(capsys, init_value, expression, expected):
    template = funcion_template(
        "main",
        [
            f"a = {init_value};",
            f"{expression};",
            "print(a);",
        ],
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == f"{expected}"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "expressions, expected",
    [
        (
            [
                "x = true;",
                conditional_template("while", "x", 'print("test"); x = false;'),
            ],
            "test",
        ),
        (
            [
                "x = 0;",
                conditional_template(
                    "while",
                    "x < 3",
                    "x += 1; print(x);",
                ),
            ],
            "123",
        ),
        (
            [
                "x = 0;",
                conditional_template(
                    "while",
                    "x < 5",
                    f'x += 1; {conditional_template("if", "x % 2 == 0", "continue;")} print(x);',
                ),
            ],
            "135",
        ),
        (
            [
                "x = Array(1, 2, 3);",
                conditional_template("for", "i : x", "print(i);"),
            ],
            "123",
        ),
        (
            [
                "x = Array(1, 2, 3, 4, 5);",
                conditional_template(
                    "for",
                    "i : x",
                    f'print(i); {conditional_template("if", "i == 3", "break;")}',
                ),
            ],
            "123",
        ),
        (
            [
                "x = Array(1, 2, 3, 4, 5);",
                conditional_template(
                    "for",
                    "i : x",
                    f'{conditional_template("if", "i % 2 == 0", "continue;")} print(i);',
                ),
            ],
            "135",
        ),
    ],
)
def test_loops(expressions, expected, capsys):
    template = funcion_template("main", expressions)
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == f"{expected}"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "expression",
    [
        "a += 2",
        'a = "x" + 1',
        "break",
        "continue",
        "a.remove(1)",
        'throw Error("error")',
    ],
)
def test_try_catch_without_params(expression, capsys):
    print_func = 'print("error");'
    template = funcion_template(
        "main",
        [
            f"{block_template('try', f'{expression};')}",
            f"{block_template('catch', print_func)}",
        ],
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == "error"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "function_names, function_params, function_bodies, expected",
    [
        (
            ["main"],
            [""],
            [
                [
                    'x = Student("John", "Doe", 20);',
                    'x.name = "Maciej";',
                    "print(x.name);",
                ]
            ],
            "Maciej",
        ),
        (
            ["main"],
            [""],
            [
                [
                    'x = Student("John", "Doe", 20);',
                    "x.age += 10;",
                    "print(x.age);",
                ]
            ],
            "30",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                [
                    conditional_template("if", "x >= 10", "return;"),
                    "print(x);",
                    "test(x + 1);",
                ],
                ["test(1);"],
            ],
            "123456789",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x = 2;"],
                ["x = 1;", "test(x);", "print(x);"],
            ],
            "1",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x = 2;"],
                ["a = 1;", "test(@a);", "print(a);"],
            ],
            "2",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x += 1;"],
                ["a = 1;", "test(a);", "print(a);"],
            ],
            "1",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x += 1;"],
                ["a = 1;", "test(@a);", "print(a);"],
            ],
            "2",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ['x.name = "Maciej";'],
                ['a = Student("John", "Doe", 20);', "test(a);", "print(a.name);"],
            ],
            "John",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ['x.name = "Maciej";'],
                ['a = Student("John", "Doe", 20);', "test(@a);", "print(a.name);"],
            ],
            "Maciej",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x.age += 10;"],
                ['a = Student("John", "Doe", 20);', "test(a);", "print(a.age);"],
            ],
            "20",
        ),
        (
            ["test", "main"],
            ["x", ""],
            [
                ["x.age += 10;"],
                ['a = Student("John", "Doe", 20);', "test(@a);", "print(a.age);"],
            ],
            "30",
        ),
        (
            ["test", "main"],
            ["", ""],
            [
                ['throw Error("Error");'],
                [
                    block_template("try", "test();"),
                    block_template("catch", 'print("caught");'),
                ],
            ],
            "caught",
        ),
        (
            ["test", "main"],
            ["", ""],
            [
                ['throw Error("Error", 1);'],
                [
                    block_template("try", "test();"),
                    conditional_template(
                        "catch",
                        "Error e",
                        'print("caught ", e.message, " ", e.args.get(0));',
                    ),
                ],
            ],
            "caught Error 1",
        ),
        (
            ["test", "main"],
            ["", ""],
            [
                ['throw Error("Error", 1, 2);'],
                [
                    block_template("try", "test();"),
                    conditional_template(
                        "catch",
                        "Error e",
                        'print("caught ", e.message, " ", e.args);',
                    ),
                ],
            ],
            "caught Error [1, 2]",
        ),
        (
            ["test", "main"],
            ["", ""],
            [
                ["x = 2;", 'throw Error("Error", 1, x);'],
                [
                    block_template("try", "test();"),
                    conditional_template(
                        "catch",
                        "Error e",
                        'print("caught ", e.message, " ", e.args);',
                    ),
                ],
            ],
            "caught Error [1, 2]",
        ),
    ],
)
def test_function_call(
    function_names, function_params, function_bodies, expected, capsys
):
    templates = [
        funcion_template(
            function_name,
            [f"{statement}" for statement in function_body],
            function_param,
        )
        for function_name, function_body, function_param in zip(
            function_names, function_bodies, function_params
        )
    ]
    error_handler = interpreter_init(templates)
    out = capsys.readouterr()
    assert out.out == expected
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "expression, expected",
    [
        (
            'x = 1 + "a"',
            TypeError,
        ),
        (
            'x = 1 - "a"',
            TypeError,
        ),
        (
            'x = 1 * "a"',
            TypeError,
        ),
        (
            'x = 1 / "a"',
            TypeError,
        ),
        (
            'x = 1 % "a"',
            TypeError,
        ),
        (
            'x = 1.0 + "a"',
            TypeError,
        ),
        (
            "x = 1.0 + true",
            TypeError,
        ),
        (
            "x = 1.0 + false",
            TypeError,
        ),
        (
            "x = 1.0 + Array()",
            TypeError,
        ),
        (
            "x = 1.0 + null",
            TypeError,
        ),
        (
            "x = 1 & 1",
            TypeError,
        ),
        (
            'x = "a" & 1',
            TypeError,
        ),
        (
            "x = 1 | 1",
            TypeError,
        ),
        (
            'x = "a" | 1',
            TypeError,
        ),
        (
            'x = !"a"',
            TypeError,
        ),
        (
            "x = !1",
            TypeError,
        ),
        (
            "x = -true",
            TypeError,
        ),
        (
            'x = -"a"',
            TypeError,
        ),
        (
            "x += 1",
            VariableError,
        ),
        (
            "x -= 1",
            VariableError,
        ),
        (
            "x *= 1",
            VariableError,
        ),
        (
            "x /= 1",
            VariableError,
        ),
        (
            "x %= 1",
            VariableError,
        ),
        (
            "test()",
            FunctionError,
        ),
        (
            "Student().test",
            PropertyError,
        ),
        (
            "Student().test()",
            PropertyError,
        ),
        ('Student("a", "a", "a", "a")', ArgumentError),
        ("main()", FunctionError),
        ("x = 1 / 0", ValueError),
        ("x = 1 % 0", ValueError),
    ],
)
def test_oneliner_errors(expression, expected):
    template = funcion_template(
        "main",
        [f"{expression};"],
    )
    error_handler = interpreter_init([template])
    assert len(error_handler.errors) == 1
    assert isinstance(error_handler.errors[0], expected)


@pytest.mark.parametrize(
    "function_names, function_bodies, function_args, expected",
    [
        ([], [], [], RuntimeError),
        (["test"], ["x = 1;"], [], RuntimeError),
        (["main"], [""], ["x"], ArgumentError),
        (["main", "test"], ["test(1);", "x /= 0;"], ["", "x"], ValueError),
        (["main", "test"], ["test(1);", "x %= 0;"], ["", "x"], ValueError),
        (["main", "test"], ["test(1);", ""], ["", ""], ArgumentError),
        (["main", "test"], ["test();", ""], ["", "x"], ArgumentError),
        (
            ["main", "test"],
            ["test();", 'throw ArgumentError("test");'],
            ["", ""],
            ArgumentError,
        ),
        (
            ["main", "test"],
            ["test();", "x += 1;"],
            ["", ""],
            VariableError,
        ),
        (
            ["main", "test"],
            ["test();", "test();"],
            ["", ""],
            StackOverflowError,
        ),
        (
            ["main", "test"],
            [conditional_template("while", "true", "test();"), "break;"],
            ["", ""],
            ExpressionError,
        ),
        (
            ["main", "test"],
            [conditional_template("while", "true", "test();"), "continue;"],
            ["", ""],
            ExpressionError,
        ),
        (
            ["main", "test"],
            [
                f'x = Array(1,2,3); \n {conditional_template("for", "i : x", "test();")}',
                "break;",
            ],
            ["", ""],
            ExpressionError,
        ),
        (
            ["main", "test"],
            [
                f'x = Array(1,2,3); \n {conditional_template("for", "i : x", "test();")}',
                "continue;",
            ],
            ["", ""],
            ExpressionError,
        ),
        (
            ["main"],
            [f'x = Array(1,2,3); \n {conditional_template("for", "x : x", "")}'],
            [""],
            VariableError,
        ),
        (
            ["main"],
            [
                f'i = "test"; x = Array(1,2,3); \n {conditional_template("for", "i : x", "")}'
            ],
            [""],
            VariableError,
        ),
    ],
)
def test_function_call_errors(function_names, function_bodies, function_args, expected):
    templates = [
        funcion_template(
            function_name,
            [f"{function_body}"],
            function_arg,
        )
        for function_name, function_body, function_arg in zip(
            function_names, function_bodies, function_args
        )
    ]
    error_handler = interpreter_init(templates)
    assert len(error_handler.errors) == 1
    assert isinstance(error_handler.errors[0], expected)
