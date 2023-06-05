import io
import pytest

from interpreter.interpreter_class import Interpreter
from lexer.lexer_class import Lexer
from parser.parser_class import Parser
from utils.error_handler_class import ErrorHandler
from interpreter.interpreter_error_classes import *


def functions_template(functions: list[str]):
    functions = "\n".join([f"    {function};" for function in functions])
    return f"""{functions}"""


def funcion_template(name, statements: list[str], arguments=""):
    statements = "\n".join([f"    {statement}" for statement in statements])
    return f"""{name}({arguments}) {{
    {statements}
}}"""


def if_template(condition, body):
    return f"""if ({condition}) {{
    {body}
}}"""


def elif_template(condition, body):
    return f"""elif ({condition}) {{
    {body}
}}"""


def else_template(body):
    return f"""else {{
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
        ("Student()?.name", None),
        ("Student()?.surname", None),
        ("Student()?.age", None),
        ("Array(1, 2)?.test()", None),
        # type checking
        ("1 is int", True),
        ("1.0 is float", True),
        ("true is bool", True),
        ("false is bool", True),
        ('"Hello World" is str', True),
        ("Array() is Array", True),
        ("Student() is Student", True),
    ],
)
def test_base_expressions(input, expected, capsys):
    error_handler = interpreter_init([funcion_template("main", [f"print({input});"])])
    out = capsys.readouterr()
    assert out.out == f"{expected} \n"
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
    template = funcion_template("main", [if_template(condition, "print(1);")])
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == "1 \n"
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "condition, expected",
    [
        ("true", "1 \n"),
        ("1 > 0", "1 \n"),
        ("1 < 2", "1 \n"),
        ("1 >= 1", "1 \n"),
        ("1 <= 1", "1 \n"),
        ("1 == 1", "1 \n"),
        ("1 != 2", "1 \n"),
        ("1.0 > 0.0", "1 \n"),
        ("1.0 < 2.0", "1 \n"),
        ("1.0 >= 1.0", "1 \n"),
        ("1.0 <= 1.0", "1 \n"),
        ("1.0 == 1.0", "1 \n"),
        ("1.0 != 2.0", "1 \n"),
        ("false", "2 \n"),
        ("1 > 2", "2 \n"),
        ("1 < 0", "2 \n"),
        ("1 >= 2", "2 \n"),
        ("1 <= 0", "2 \n"),
        ("1 == 2", "2 \n"),
        ("1 != 1", "2 \n"),
        ("1.0 > 2.0", "2 \n"),
        ("1.0 < 0.0", "2 \n"),
        ("1.0 >= 2.0", "2 \n"),
        ("1.0 <= 0.0", "2 \n"),
        ("1.0 == 2.0", "2 \n"),
        ("1.0 != 1.0", "2 \n"),
    ],
)
def test_if_else_statement(capsys, condition, expected):
    template = funcion_template(
        "main", [if_template(condition, "print(1);"), else_template("print(2);")]
    )
    error_handler = interpreter_init([template])
    out = capsys.readouterr()
    assert out.out == expected
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "init_value, expression, expected",
    [
        # value change
        ("1", "a = 2", "2 \n"),
        ("1", "a = 2.0", "2.0 \n"),
        ("1", "a = true", "True \n"),
        ("1", "a = false", "False \n"),
        ("1", 'a = "Hello"', "Hello \n"),
        ("1", "a = Array()", "[] \n"),
        ("1", "a = Array(1)", "[1] \n"),
        ("1", "a = Array(1, 2)", "[1, 2] \n"),
        # value change with operations
        ("1", "a += 2", "3 \n"),
        ("1", "a += 2.0", "3.0 \n"),
        ("1", "a -= 2", "-1 \n"),
        ("1", "a -= 2.0", "-1.0 \n"),
        ("1", "a *= 2", "2 \n"),
        ("1", "a *= 2.0", "2.0 \n"),
        ("1", "a /= 2", "0.5 \n"),
        ("1", "a /= 2.0", "0.5 \n"),
        ("1", "a %= 2", "1 \n"),
        ("1", "a %= 2.0", "1.0 \n"),
        # array operations
        ("Array()", "a.add(1)", "[1] \n"),
        ("Array(1)", "a.add(2)", "[1, 2] \n"),
        ("Array(3, 2, 1)", "a.remove(1)", "[3, 2] \n"),
        ("Array(3, 2, 1)", "a.remove(2)", "[3, 1] \n"),
        ("Array(3, 2, 1)", "a.removeAt(0)", "[2, 1] \n"),
        ("Array(3, 2, 1)", "a.removeAt(1)", "[3, 1] \n"),
        ("Array(3, 2, 1)", "a.clear()", "[] \n"),
        ("Array(3, 2, 1)", "a = a.size()", "3 \n"),
        ("Array(3, 2, 1)", "a = a.get(0)", "3 \n"),
        ("Array(3, 2, 1)", "a = a.get(1)", "2 \n"),
        ("Array(3, 2, 1)", "a.set(0, 1)", "[1, 2, 1] \n"),
        ("Array(3, 2, 1)", "a.set(1, 3)", "[3, 3, 1] \n"),
        ("Array(3, 2, 1)", "a = a.contains(1)", "True \n"),
        ("Array(3, 2, 1)", "a = a.contains(4)", "False \n"),
        ("Array(3, 2, 1)", "a = a.indexOf(3)", "0 \n"),
        ("Array(3, 2, 1)", "a = a.indexOf(2)", "1 \n"),
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
    assert out.out == expected
    assert len(error_handler.errors) == 0


@pytest.mark.parametrize(
    "function_names, function_bodies, function_args,expected",
    [
        (
            ["main", "test"],
            [["test();"], ["print(1);"]],
            ["", ""],
            "1 \n",
        )
    ],
)
def test_function_calls(
    capsys, function_names, function_bodies, function_args, expected
):
    templates = [
        funcion_template(
            function_name,
            function_body,
            function_arg,
        )
        for function_name, function_body, function_arg in zip(
            function_names, function_bodies, function_args
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
            'x = 1 + "a";',
            TypeError,
        ),
        (
            'x = 1 - "a";',
            TypeError,
        ),
        (
            'x = 1 * "a";',
            TypeError,
        ),
        (
            'x = 1 / "a";',
            TypeError,
        ),
        (
            'x = 1 % "a";',
            TypeError,
        ),
        (
            'x = 1.0 + "a";',
            TypeError,
        ),
        (
            "x = 1.0 + true;",
            TypeError,
        ),
        (
            "x = 1.0 + false;",
            TypeError,
        ),
        (
            "x = 1.0 + Array();",
            TypeError,
        ),
        (
            "x = 1.0 + null;",
            TypeError,
        ),
        (
            "x = 1 & 1;",
            TypeError,
        ),
        (
            'x = "a" & 1;',
            TypeError,
        ),
        (
            "x = 1 | 1;",
            TypeError,
        ),
        (
            'x = "a" | 1;',
            TypeError,
        ),
        (
            'x = !"a";',
            TypeError,
        ),
        (
            "x = !1;",
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
            "x += 1;",
            VariableError,
        ),
        (
            "x -= 1;",
            VariableError,
        ),
        (
            "x *= 1;",
            VariableError,
        ),
        (
            "x /= 1;",
            VariableError,
        ),
        (
            "x %= 1;",
            VariableError,
        ),
        (
            "test();",
            FunctionError,
        ),
        (
            "Student().test;",
            PropertyError,
        ),
        (
            "Student().test();",
            PropertyError,
        ),
        ('Student("a", "a", "a", "a");', PropertyError),
    ],
)
def test_oneliner_errors(expression, expected):
    template = funcion_template(
        "main",
        [expression],
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        error_handler = interpreter_init([template])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        assert len(error_handler.errors) == 1
        assert isinstance(error_handler.errors[0], expected)


@pytest.mark.parametrize(
    "function_names, function_bodies, function_args, expected",
    [
        ([], [], [], RuntimeError),
        (["test"], ["x = 1;"], [], RuntimeError),
        (["main", "test"], ["test(1);", ""], ["", ""], ArgumentError),
        (["main", "test"], ["test();", ""], ["", "1"], ArgumentError),
        (
            ["main", "test"],
            ["test();", 'throw ArgumentError("test")'],
            ["", ""],
            ArgumentError,
        ),
        (
            ["main", "test"],
            ["test();", "x += 1;"],
            ["", ""],
            VariableError,
        ),
    ],
)
def test_function_call_errors(function_names, function_bodies, function_args, expected):
    templates = [
        funcion_template(
            function_name,
            [function_body],
            function_arg,
        )
        for function_name, function_body, function_arg in zip(
            function_names, function_bodies, function_args
        )
    ]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        error_handler = interpreter_init(templates)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        assert len(error_handler.errors) == 1
        assert isinstance(error_handler.errors[0], expected)
