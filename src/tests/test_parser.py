import io
import pytest

from lexer.lexer_class import Lexer
from parser.parser_class import Parser
from parser.statement_classes import *
from lexer.token_type_enum import TokenType
from utils.error_handler_class import ErrorHandler
from parser.parser_error_class import PARSER_ERROR_TYPES


def program_template(parameters="", statements=""):
    return f"main({parameters}){{{statements}}}"


def while_statement_template(condition, block=""):
    return f"while ({condition}) {{{block}}}"


def if_statement_template(condition, block=""):
    return f"if ({condition}) {{{block}}}"


def elif_statement_template(condition, block=""):
    return f"elif ({condition}) {{{block}}}"


def return_statement_template(expression):
    return f"return {expression};"


def test_init():
    error_handler = ErrorHandler()
    with io.StringIO("") as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        assert parser.lexer == lexer
        assert parser.current_token.type == TokenType.T_EOF


@pytest.mark.parametrize(
    "input, result",
    [
        # basic
        (r"param", [Parameter("param")]),
        (r"param?", [Parameter("param", is_optional=True)]),
        (
            r'param? = "a"',
            [Parameter("param", is_optional=True, value=StringLiteral("a"))],
        ),
        (
            r"param? = 1",
            [Parameter("param", is_optional=True, value=IntegerLiteral(1))],
        ),
        (
            r"param? = 1.1",
            [Parameter("param", is_optional=True, value=FloatLiteral(1.1))],
        ),
        (
            r"param? = false",
            [Parameter("param", is_optional=True, value=FalseLiteral())],
        ),
        (r"param? = true", [Parameter("param", is_optional=True, value=TrueLiteral())]),
        # multiple parameters
        (r"param1, param2", [Parameter("param1"), Parameter("param2")]),
        (
            r"param1, param2?",
            [Parameter("param1"), Parameter("param2", is_optional=True)],
        ),
        (
            r"param1, param2? = 1",
            [
                Parameter("param1"),
                Parameter("param2", is_optional=True, value=IntegerLiteral(1)),
            ],
        ),
        (
            r"param1, param2? = 1.1",
            [
                Parameter("param1"),
                Parameter("param2", is_optional=True, value=FloatLiteral(1.1)),
            ],
        ),
        (
            r'param1, param2? = "a"',
            [
                Parameter("param1"),
                Parameter("param2", is_optional=True, value=StringLiteral("a")),
            ],
        ),
        (
            r"param1, param2? = false",
            [
                Parameter("param1"),
                Parameter("param2", is_optional=True, value=FalseLiteral()),
            ],
        ),
        (
            r"param1, param2? = true",
            [
                Parameter("param1"),
                Parameter("param2", is_optional=True, value=TrueLiteral()),
            ],
        ),
    ],
)
def test_function_parameters(input, result):
    error_handler = ErrorHandler()
    final_input = program_template(parameters=input)
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        program = parser.parse()
    for parameter, res in zip(program.functions["main"].parameters, result):
        assert parameter == res


@pytest.mark.parametrize(
    "statement_template, statement_class",
    [
        (while_statement_template, WhileStatement),
        (if_statement_template, IfStatement),
        (return_statement_template, ReturnStatement),
    ],
)
@pytest.mark.parametrize(
    "condition_input, condition_result",
    [
        # single expression
        (
            r"1 | 2",
            OrExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 & 2",
            AndExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 == 2",
            EqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 != 2",
            NotEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 > 2",
            GreaterThanExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 >= 2",
            GreaterEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 < 2",
            LessThanExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 <= 2",
            LessEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 + 2",
            AddExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 - 2",
            SubtractExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 * 2",
            MultiplyExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 / 2",
            DivideExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            r"1 % 2",
            ModuloExpression(IntegerLiteral(1), IntegerLiteral(2)),
        ),
        (
            "!1",
            BitwiseNegationExpression(IntegerLiteral(1)),
        ),
        (
            "-1",
            NumericNegationExpression(IntegerLiteral(1)),
        ),
        (
            r"1 is Int",
            TypeCheckExpression(IntegerLiteral(1), IdentifierExpression("Int")),
        ),
        (r"x", IdentifierExpression("x")),
        (r"x()", FunctionCallExpression("x", [])),
        (r"x(1)", FunctionCallExpression("x", [Argument(IntegerLiteral(1))])),
        (r"x(y)", FunctionCallExpression("x", [Argument(IdentifierExpression("y"))])),
        (
            r"x(@y)",
            FunctionCallExpression(
                "x", [Argument(IdentifierExpression("y"), is_reference=True)]
            ),
        ),
        (
            r"x.y",
            PropertyAccessExpression(
                IdentifierExpression("x"), IdentifierExpression("y")
            ),
        ),
        (
            r"x.y()",
            PropertyAccessExpression(
                IdentifierExpression("x"), FunctionCallExpression("y", [])
            ),
        ),
        (
            r"x.y(1)",
            PropertyAccessExpression(
                IdentifierExpression("x"),
                FunctionCallExpression("y", [Argument(IntegerLiteral(1))]),
            ),
        ),
        (
            r"x().y",
            PropertyAccessExpression(
                FunctionCallExpression("x", []), IdentifierExpression("y")
            ),
        ),
        (
            r"x?.y",
            OptionalPropertyAccessExpression(
                IdentifierExpression("x"), IdentifierExpression("y")
            ),
        ),
        (
            r"x?.y()",
            OptionalPropertyAccessExpression(
                IdentifierExpression("x"), FunctionCallExpression("y", [])
            ),
        ),
        (
            r"x?.y(1)",
            OptionalPropertyAccessExpression(
                IdentifierExpression("x"),
                FunctionCallExpression("y", [Argument(IntegerLiteral(1))]),
            ),
        ),
        (
            r"x()?.y",
            OptionalPropertyAccessExpression(
                FunctionCallExpression("x", []), IdentifierExpression("y")
            ),
        ),
        # multiple expressions
        (
            r"1 | 2 | 3",
            OrExpression(
                OrExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 & 2 & 3",
            AndExpression(
                AndExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 == 2 == 3",
            EqualExpression(
                EqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 != 2 != 3",
            NotEqualExpression(
                NotEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 > 2 > 3",
            GreaterThanExpression(
                GreaterThanExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 >= 2 >= 3",
            GreaterEqualExpression(
                GreaterEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 < 2 < 3",
            LessThanExpression(
                LessThanExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 <= 2 <= 3",
            LessEqualExpression(
                LessEqualExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 + 2 + 3",
            AddExpression(
                AddExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 - 2 - 3",
            SubtractExpression(
                SubtractExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 * 2 * 3",
            MultiplyExpression(
                MultiplyExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 / 2 / 3",
            DivideExpression(
                DivideExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 % 2 % 3",
            ModuloExpression(
                ModuloExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"x.y.z()",
            PropertyAccessExpression(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                FunctionCallExpression("z", []),
            ),
        ),
        (
            r"x.y().z",
            PropertyAccessExpression(
                PropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("y", [])
                ),
                IdentifierExpression("z"),
            ),
        ),
        (
            r"x.y?.z()",
            OptionalPropertyAccessExpression(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                FunctionCallExpression("z", []),
            ),
        ),
        (
            r"x?.y().z",
            PropertyAccessExpression(
                OptionalPropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("y", [])
                ),
                IdentifierExpression("z"),
            ),
        ),
        # operator precedence
        (
            r"1 + 2 * 3",
            AddExpression(
                IntegerLiteral(1),
                MultiplyExpression(IntegerLiteral(2), IntegerLiteral(3)),
            ),
        ),
        (
            r"1 * 2 + 3",
            AddExpression(
                MultiplyExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 | 2 & 3",
            OrExpression(
                IntegerLiteral(1),
                AndExpression(IntegerLiteral(2), IntegerLiteral(3)),
            ),
        ),
        (
            r"1 & 2 | 3",
            OrExpression(
                AndExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
        (
            r"1 + 2 == 3 * 1",
            EqualExpression(
                AddExpression(IntegerLiteral(1), IntegerLiteral(2)),
                MultiplyExpression(IntegerLiteral(3), IntegerLiteral(1)),
            ),
        ),
        (
            r"(1 + 2) * 3",
            MultiplyExpression(
                AddExpression(IntegerLiteral(1), IntegerLiteral(2)),
                IntegerLiteral(3),
            ),
        ),
    ],
)
def test_expression(
    statement_template,
    statement_class,
    condition_input,
    condition_result,
):
    error_handler = ErrorHandler()
    final_input = program_template(statements=statement_template(condition_input))
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        program = parser.parse()
    expression_class = program.functions["main"].block.statements[0]
    if getattr(expression_class, "block", None) is None:
        res_expression = statement_class(condition_result)
    else:
        res_expression = statement_class(condition_result, BlockStatement([]))
    assert expression_class == res_expression


@pytest.mark.parametrize(
    "input, result",
    [
        ("break;", BreakStatement()),
        ("continue;", ContinueStatement()),
        ("return;", ReturnStatement()),
        ("x;", IdentifierExpression("x")),
        ("x();", FunctionCallExpression("x", [])),
        ("x(1);", FunctionCallExpression("x", [Argument(IntegerLiteral(1))])),
        (
            "x(-1);",
            FunctionCallExpression(
                "x", [Argument(NumericNegationExpression(IntegerLiteral(1)))]
            ),
        ),
        (
            "x(y.z);",
            FunctionCallExpression(
                "x",
                [
                    Argument(
                        PropertyAccessExpression(
                            IdentifierExpression("y"), IdentifierExpression("z")
                        )
                    )
                ],
            ),
        ),
        (
            "x(y.z());",
            FunctionCallExpression(
                "x",
                [
                    Argument(
                        PropertyAccessExpression(
                            IdentifierExpression("y"), FunctionCallExpression("z", [])
                        )
                    )
                ],
            ),
        ),
        (
            "x(y().z);",
            FunctionCallExpression(
                "x",
                [
                    Argument(
                        PropertyAccessExpression(
                            FunctionCallExpression("y", []), IdentifierExpression("z")
                        )
                    )
                ],
            ),
        ),
        ("x = 1;", AssignmentStatement(IdentifierExpression("x"), IntegerLiteral(1))),
        (
            "x += 1;",
            AssignmentPlusStatement(IdentifierExpression("x"), IntegerLiteral(1)),
        ),
        (
            "x -= 1;",
            AssignmentMinusStatement(IdentifierExpression("x"), IntegerLiteral(1)),
        ),
        (
            "x *= 1;",
            AssignmentMultiplyStatement(IdentifierExpression("x"), IntegerLiteral(1)),
        ),
        (
            "x /= 1;",
            AssignmentDivideStatement(IdentifierExpression("x"), IntegerLiteral(1)),
        ),
        (
            "x %= 1;",
            AssignmentModuloStatement(IdentifierExpression("x"), IntegerLiteral(1)),
        ),
        (
            "x = 1 + 2;",
            AssignmentStatement(
                IdentifierExpression("x"),
                AddExpression(IntegerLiteral(1), IntegerLiteral(2)),
            ),
        ),
        (
            "x = 1 + 2 * 3;",
            AssignmentStatement(
                IdentifierExpression("x"),
                AddExpression(
                    IntegerLiteral(1),
                    MultiplyExpression(IntegerLiteral(2), IntegerLiteral(3)),
                ),
            ),
        ),
        (
            "x = y();",
            AssignmentStatement(
                IdentifierExpression("x"), FunctionCallExpression("y", [])
            ),
        ),
        (
            "x = y(1);",
            AssignmentStatement(
                IdentifierExpression("x"),
                FunctionCallExpression("y", [Argument(IntegerLiteral(1))]),
            ),
        ),
        (
            r"x = y.z;",
            AssignmentStatement(
                IdentifierExpression("x"),
                PropertyAccessExpression(
                    IdentifierExpression("y"), IdentifierExpression("z")
                ),
            ),
        ),
        (
            "try {} catch {}",
            TryCatchStatement(BlockStatement([]), [CatchStatement(BlockStatement([]))]),
        ),
        (
            "try {} catch (Error e) {}",
            TryCatchStatement(
                BlockStatement([]),
                [
                    CatchStatement(
                        BlockStatement([]),
                        [IdentifierExpression("Error")],
                        IdentifierExpression("e"),
                    )
                ],
            ),
        ),
        (
            "try {} catch (FirstError | SecondError e) {}",
            TryCatchStatement(
                BlockStatement([]),
                [
                    CatchStatement(
                        BlockStatement([]),
                        [
                            IdentifierExpression("FirstError"),
                            IdentifierExpression("SecondError"),
                        ],
                        IdentifierExpression("e"),
                    )
                ],
            ),
        ),
        (
            "try {} catch (FirstError e) {} catch (SecondError e) {})",
            TryCatchStatement(
                BlockStatement([]),
                [
                    CatchStatement(
                        BlockStatement([]),
                        [
                            IdentifierExpression("FirstError"),
                        ],
                        IdentifierExpression("e"),
                    ),
                    CatchStatement(
                        BlockStatement([]),
                        [
                            IdentifierExpression("SecondError"),
                        ],
                        IdentifierExpression("e"),
                    ),
                ],
            ),
        ),
        (
            r"throw Error;",
            ThrowStatement(IdentifierExpression("Error")),
        ),
        (
            r'throw Error("Error");',
            ThrowStatement(
                FunctionCallExpression("Error", [Argument(StringLiteral("Error"))])
            ),
        ),
        (
            r"if (true) {}",
            IfStatement(BooleanLiteral(True), BlockStatement([])),
        ),
        (
            r"if (true) {} else {}",
            IfStatement(
                BooleanLiteral(True),
                BlockStatement([]),
                else_statement=BlockStatement([]),
            ),
        ),
        (
            r"if (true) {} elif (false) {}",
            IfStatement(
                BooleanLiteral(True),
                BlockStatement([]),
                elif_statements=[
                    ConditionalStatement(BooleanLiteral(False), BlockStatement([]))
                ],
            ),
        ),
        (
            r"if (x) {} elif (y) {} elif(z) {} else {}",
            IfStatement(
                IdentifierExpression("x"),
                BlockStatement([]),
                elif_statements=[
                    ConditionalStatement(IdentifierExpression("y"), BlockStatement([])),
                    ConditionalStatement(IdentifierExpression("z"), BlockStatement([])),
                ],
                else_statement=BlockStatement([]),
            ),
        ),
        (
            r"while (true) {}",
            WhileStatement(BooleanLiteral(True), BlockStatement([])),
        ),
        (
            "for (i: x) {}",
            ForStatement(
                IdentifierExpression("i"),
                IdentifierExpression("x"),
                BlockStatement([]),
            ),
        ),
    ],
)
def test_statements(input, result):
    error_handler = ErrorHandler()
    final_input = program_template(statements=input)
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        program = parser.parse()
    statement_class = program.functions["main"].block.statements[0]
    assert statement_class == result


@pytest.mark.parametrize(
    "input, expected_error",
    [
        # Missing expressions
        ("x = 1 +;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = 1 -;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = 1 *;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = 1 /;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = 1 %;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y == ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y != ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y < ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y > ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y <= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y >= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y & ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y | ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x += ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x -= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x *= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x /= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x %= ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y.;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("x = y().;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        ("throw ;", PARSER_ERROR_TYPES.MISSING_EXPRESSION),
        # Conditional statements
        ("if", PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET),
        ("if (", PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION),
        ("if (true", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("if (true)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("if (true) {} else", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("if (true) {} elif", PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET),
        ("if (true) {} elif (", PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION),
        ("if (true) {} elif (true", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("if (true) {} elif (true)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("while", PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET),
        ("while (", PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION),
        ("while (true", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("while (true)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        # For loop
        ("for", PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET),
        ("for (", PARSER_ERROR_TYPES.MISSING_FOR_LOOP_VARIABLE),
        ("for (i", PARSER_ERROR_TYPES.MISSING_FOR_LOOP_COLON),
        ("for (i:", PARSER_ERROR_TYPES.MISSING_FOR_LOOP_ITERABLE),
        ("for (i: x", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("for (i: x)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        # Try statement
        ("try", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("try {}", PARSER_ERROR_TYPES.MISSING_CATCH_KEYWORD),
        ("try {} catch", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("try {} catch (", PARSER_ERROR_TYPES.MISSING_ERROR_TYPE),
        ("try {} catch (Error", PARSER_ERROR_TYPES.MISSING_ERROR_VARIABLE),
        ("try {} catch (Error e", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("try {} catch (Error e)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        ("try {} catch (Error1 |", PARSER_ERROR_TYPES.MISSING_ERROR_TYPE),
        ("try {} catch (Error1 | Error2", PARSER_ERROR_TYPES.MISSING_ERROR_VARIABLE),
        ("try {} catch (Error1 | Error2 e", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("try {} catch (Error1 | Error2 e)", PARSER_ERROR_TYPES.MISSING_BLOCK_START),
        # Type check expression
        ("x = y is;", PARSER_ERROR_TYPES.MISSING_TYPE_NAME),
        # Function call
        ("x(a;", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        ("x(a,;", PARSER_ERROR_TYPES.MISSING_ARGUMENT),
        ("x(a, b;", PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET),
        # Missing semicolon
        ("x = 1 + 2", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = 1 - 2", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = 1 * 2", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = 1 / 2", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = 1 % 2", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y == 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y != 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y < 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y > 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y <= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y >= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y & 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y | 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x += 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x -= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x *= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x /= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x %= 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y.z", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y.z()", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("x = y is Int", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("return", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("return 1", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("continue", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
        ("break", PARSER_ERROR_TYPES.MISSING_SEMICOLON),
    ],
)
def test_error_handling(input, expected_error):
    error_handler = ErrorHandler()
    final_input = program_template(statements=input)
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        parser.parse()
    assert error_handler.has_errors()
    assert error_handler.errors[0].type == expected_error


@pytest.mark.parametrize(
    "input, expected_result",
    [
        (
            "x = y.z;",
            AssignmentStatement(
                IdentifierExpression("x"),
                PropertyAccessExpression(
                    IdentifierExpression("y"), IdentifierExpression("z")
                ),
            ),
        ),
        (
            "x = y.z();",
            AssignmentStatement(
                IdentifierExpression("x"),
                PropertyAccessExpression(
                    IdentifierExpression("y"),
                    FunctionCallExpression("z", []),
                ),
            ),
        ),
        (
            "x.y = z;",
            AssignmentStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                IdentifierExpression("z"),
            ),
        ),
        (
            "x.y = z();",
            AssignmentStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                FunctionCallExpression("z", []),
            ),
        ),
        (
            "x.y = x.z;",
            AssignmentStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("z")
                ),
            ),
        ),
        (
            "x.y = x.z();",
            AssignmentStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                PropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("z", [])
                ),
            ),
        ),
        (
            "x(y.z);",
            FunctionCallExpression(
                "x",
                [
                    Argument(
                        PropertyAccessExpression(
                            IdentifierExpression("y"), IdentifierExpression("z")
                        )
                    )
                ],
            ),
        ),
        (
            "x(y.z());",
            FunctionCallExpression(
                "x",
                [
                    Argument(
                        PropertyAccessExpression(
                            IdentifierExpression("y"), FunctionCallExpression("z", [])
                        )
                    )
                ],
            ),
        ),
        (
            "if (x.y) {}",
            IfStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                BlockStatement([]),
            ),
        ),
        (
            "if (x.y()) {}",
            IfStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("y", [])
                ),
                BlockStatement([]),
            ),
        ),
        (
            "if (x.y) {} elif (x.z) {}",
            IfStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                BlockStatement([]),
                [
                    ConditionalStatement(
                        PropertyAccessExpression(
                            IdentifierExpression("x"), IdentifierExpression("z")
                        ),
                        BlockStatement([]),
                    )
                ],
            ),
        ),
        (
            "if (x.y()) {} elif (x.z()) {}",
            IfStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("y", [])
                ),
                BlockStatement([]),
                [
                    ConditionalStatement(
                        PropertyAccessExpression(
                            IdentifierExpression("x"), FunctionCallExpression("z", [])
                        ),
                        BlockStatement([]),
                    )
                ],
            ),
        ),
        (
            "while (x.y) {}",
            WhileStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), IdentifierExpression("y")
                ),
                BlockStatement([]),
            ),
        ),
        (
            "while (x.y()) {}",
            WhileStatement(
                PropertyAccessExpression(
                    IdentifierExpression("x"), FunctionCallExpression("y", [])
                ),
                BlockStatement([]),
            ),
        ),
        (
            "for (x : y.z) {}",
            ForStatement(
                IdentifierExpression("x"),
                PropertyAccessExpression(
                    IdentifierExpression("y"), IdentifierExpression("z")
                ),
                BlockStatement([]),
            ),
        ),
        (
            "for (x : y.z()) {}",
            ForStatement(
                IdentifierExpression("x"),
                PropertyAccessExpression(
                    IdentifierExpression("y"), FunctionCallExpression("z", [])
                ),
                BlockStatement([]),
            ),
        ),
    ],
)
def test_access_operator(input, expected_result):
    error_handler = ErrorHandler()
    final_input = program_template(statements=input)
    with io.StringIO(final_input) as stream_provider:
        lexer = Lexer(stream_provider, error_handler)
        parser = Parser(lexer)
        program = parser.parse()
    assert not error_handler.has_errors()
    statement_class = program.functions["main"].block.statements[0]
    assert statement_class == expected_result
