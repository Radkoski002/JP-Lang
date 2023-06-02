from lexer.lexer_class import Lexer
from program.program_class import Program
from parser.statement_classes import *
from lexer.token_class import Token
from lexer.token_type_enum import TokenType
from parser.helpers import *
from parser.parser_error_class import PARSER_ERROR_TYPES, ParserError


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.error_handler = lexer.error_handler
        self.current_token: Token = lexer.build_next_token()

        self.infix_expression_params: dict[INFIX_EXPRESSIONS] = {
            INFIX_EXPRESSIONS.OR: self.__create_infix_expression_param(
                self.__parse_and_expression, or_token_to_constructor
            ),
            INFIX_EXPRESSIONS.AND: self.__create_infix_expression_param(
                self.__parse_comparation_expression,
                and_token_to_constructor,
            ),
            INFIX_EXPRESSIONS.COMPARISON: self.__create_infix_expression_param(
                self.__parse_addition_expression,
                comparison_token_to_constructor,
            ),
            INFIX_EXPRESSIONS.ADDITION: self.__create_infix_expression_param(
                self.__parse_multiplication_expression, additive_token_to_constructor
            ),
            INFIX_EXPRESSIONS.MULTIPLICATION: self.__create_infix_expression_param(
                self.__parse_negation_expression, multiplicative_token_to_constructor
            ),
            INFIX_EXPRESSIONS.PROPERTY_ACCESS: self.__create_infix_expression_param(
                self.__parse_identifier_or_function_call, access_token_to_constructor
            ),
        }

    ############################## UTILS ##############################

    @staticmethod
    def __create_infix_expression_param(
        function, constructor_dict: dict[IExpression]
    ) -> dict:
        return {
            "function": function,
            "constructor_dict": constructor_dict,
        }

    def __expect_block(self):
        block = self.__parse_block_statement()
        if not block:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_BLOCK_START)
        return block

    def __expect_token_type(self, token_type: TokenType) -> None:
        if not self.__consume_if(token_type):
            self.__add_error(token_to_error[token_type])

    def __expect_expression(
        self, expression_func, error_type: PARSER_ERROR_TYPES
    ) -> IExpression:
        if not (expression := expression_func()):
            self.__add_error(error_type)
        return expression

    def __add_error(self, error_type: PARSER_ERROR_TYPES) -> None:
        self.error_handler.add_error(
            ParserError(error_type, self.current_token.position)
        )

    def __check_token_type(self, token_type: TokenType) -> bool:
        return self.current_token.type == token_type

    def __consume_if(self, token_type: TokenType) -> bool:
        if self.__check_token_type(token_type):
            self.__next_token()
            return True
        return False

    def __next_token(self) -> None:
        self.current_token = self.lexer.build_next_token_without_comments()

    ############################## EXPRESSIONS ##############################

    def __parse_infix_expression(
        self, expression_type: INFIX_EXPRESSIONS
    ) -> IExpression:
        func_params = self.infix_expression_params[expression_type]
        left = func_params["function"]()
        if not left:
            return None
        while construtor := func_params["constructor_dict"].get(
            self.current_token.type
        ):
            position = self.current_token.position
            self.__next_token()
            right = self.__expect_expression(
                func_params["function"], PARSER_ERROR_TYPES.MISSING_EXPRESSION
            )
            left = construtor(left, right, position)
        return left

    def __parse_property_access_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.PROPERTY_ACCESS)

    def __parse_arguments(self) -> list[IExpression]:
        position = self.current_token.position
        is_reference = self.__consume_if(TokenType.T_REF)
        argument = self.__parse_expression()
        if not argument:
            return []
        arguments = [Argument(argument, is_reference, position)]
        while self.__consume_if(TokenType.T_COMMA):
            position = self.current_token.position
            is_reference = self.__consume_if(TokenType.T_REF)
            argument = self.__expect_expression(
                self.__parse_expression, PARSER_ERROR_TYPES.MISSING_ARGUMENT
            )
            arguments.append(Argument(argument, is_reference, position))
        return arguments

    def __parse_rest_of_function_call(
        self, name: str, position: Position
    ) -> IExpression:
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            return None
        arguments = self.__parse_arguments()
        self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
        return FunctionCallExpression(name, arguments, position)

    def __parse_identifier_or_function_call(self) -> IExpression:
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            return None

        name = self.current_token.value
        position = self.current_token.position
        self.__next_token()

        expression = self.__parse_rest_of_function_call(name, position)
        if not expression:
            return IdentifierExpression(name, position)
        return expression

    def __parse_expression_in_brackets(self) -> IExpression:
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            return None
        expression = self.__expect_expression(
            self.__parse_expression, PARSER_ERROR_TYPES.MISSING_EXPRESSION
        )
        self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
        return expression

    def __parse_base_expression(self):
        if constructor := literal_with_value_token_to_constructor.get(
            self.current_token.type
        ):
            expression = constructor(
                self.current_token.value, self.current_token.position
            )
            self.__next_token()
        elif self.__check_token_type(TokenType.T_IDENTIFIER):
            expression = self.__parse_property_access_expression()
        elif constructor := literal_without_value_token_to_constructor.get(
            self.current_token.type
        ):
            expression = constructor(self.current_token.position)
            self.__next_token()
        else:
            expression = self.__parse_expression_in_brackets()
        return expression

    def __parse_type_check_expression(self) -> IExpression:
        expression = self.__parse_base_expression()
        position = self.current_token.position
        if not expression:
            return None
        if not self.__consume_if(TokenType.T_TYPE_CHECK):
            return expression
        self.__expect_token_type(TokenType.T_IDENTIFIER)
        type_name = self.current_token.value
        self.__next_token()
        return TypeCheckExpression(expression, type_name, position)

    def __parse_negation_expression(self) -> IExpression:
        if constructor := negation_token_to_constructor.get(self.current_token.type):
            position = self.current_token.position
            self.__next_token()
            expression = self.__expect_expression(
                self.__parse_expression, PARSER_ERROR_TYPES.MISSING_EXPRESSION
            )
            return constructor(expression, position)
        return self.__parse_type_check_expression()

    def __parse_multiplication_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.MULTIPLICATION)

    def __parse_addition_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.ADDITION)

    def __parse_comparation_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.COMPARISON)

    def __parse_and_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.AND)

    def __parse_or_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.OR)

    def __parse_expression(self) -> IExpression:
        return self.__parse_or_expression()

    ############################## STATEMENTS ##############################

    def __parse_block_statement(self) -> BlockStatement:
        position = self.current_token.position
        if not self.__consume_if(TokenType.T_LEFT_CURLY_BRACKET):
            return None
        statements: list[IStatement] = []
        while (statement := self.__parse_statement()) is not None:
            statements.append(statement)
        self.__expect_token_type(TokenType.T_RIGHT_CURLY_BRACKET)
        return BlockStatement(statements, position)

    def __parse_condition(self) -> IExpression:
        self.__expect_token_type(TokenType.T_LEFT_BRACKET)
        condition = self.__expect_expression(
            self.__parse_expression, PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION
        )
        self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
        return condition

    def __parse_if_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_IF):
            return None
        elif_statements: list[BlockStatement] = []
        else_statement: BlockStatement = None
        condition = self.__parse_condition()
        statement = self.__expect_block()
        while self.__consume_if(TokenType.T_ELIF):
            elif_position = self.current_token.position
            elif_condition = self.__expect_expression(
                self.__parse_condition,
                PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION,
            )
            elif_statement = self.__expect_block()
            elif_statements.append(
                ConditionalStatement(elif_condition, elif_statement, elif_position)
            )
        if self.__consume_if(TokenType.T_ELSE):
            else_statement = self.__expect_block()
        return IfStatement(
            condition, statement, elif_statements, else_statement, position
        )

    def __parse_while_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_WHILE):
            return None
        condition = self.__expect_expression(
            self.__parse_condition, PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION
        )
        statement = self.__expect_block()
        return WhileStatement(condition, statement, position)

    def __parse_for_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_FOR):
            return None
        self.__expect_token_type(TokenType.T_LEFT_BRACKET)
        variable_name = self.__expect_expression(
            self.__parse_expression, PARSER_ERROR_TYPES.MISSING_FOR_LOOP_VARIABLE
        )
        self.__expect_token_type(TokenType.T_COLON)
        iterable = self.__expect_expression(
            self.__parse_property_access_expression,
            PARSER_ERROR_TYPES.MISSING_FOR_LOOP_ITERABLE,
        )
        self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
        statement = self.__expect_block()
        return ForStatement(variable_name, iterable, statement, position)

    def __parse_return_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_RETURN):
            return None
        expression = self.__parse_expression()
        self.__expect_token_type(TokenType.T_SEMICOLON)
        return ReturnStatement(expression, position)

    def __parse_variable_statement(self, position: Position) -> IStatement:
        identifier_or_fun_call = self.__parse_property_access_expression()
        if not identifier_or_fun_call:
            return None
        if constructor := assignment_token_to_constructor.get(self.current_token.type):
            self.__next_token()
            expression = self.__expect_expression(
                self.__parse_expression, PARSER_ERROR_TYPES.MISSING_EXPRESSION
            )
            self.__expect_token_type(TokenType.T_SEMICOLON)
            return constructor(identifier_or_fun_call, expression, position)
        else:
            self.__expect_token_type(TokenType.T_SEMICOLON)
            return identifier_or_fun_call

    def __parse_catch_statements(self) -> IStatement:
        catch_statements: list[CatchStatement] = []
        position = self.current_token.position
        while self.__consume_if(TokenType.T_CATCH):
            exception_types: list[IdentifierExpression] = []
            variable_name: IdentifierExpression = None
            if self.__consume_if(TokenType.T_LEFT_BRACKET):
                exception_type = self.__expect_expression(
                    self.__parse_identifier_or_function_call,
                    PARSER_ERROR_TYPES.MISSING_ERROR_TYPE,
                )
                exception_types = [exception_type]
                while self.__consume_if(TokenType.T_OR):
                    error_type = self.__expect_expression(
                        self.__parse_identifier_or_function_call,
                        PARSER_ERROR_TYPES.MISSING_ERROR_TYPE,
                    )
                    exception_types.append(error_type)
                variable_name = self.__expect_expression(
                    self.__parse_identifier_or_function_call,
                    PARSER_ERROR_TYPES.MISSING_ERROR_VARIABLE,
                )
                self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
            catch_statements.append(
                CatchStatement(
                    self.__expect_block(), exception_types, variable_name, position
                )
            )
            position = self.current_token.position
        if len(catch_statements) == 0:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CATCH_KEYWORD)
        return catch_statements

    def __parse_try_catch_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_TRY):
            return None
        try_statement = self.__expect_block()
        catch_statements = self.__parse_catch_statements()
        return TryCatchStatement(try_statement, catch_statements, position)

    def __parse_throw_exception_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_THROW):
            return None
        thrown_expression = self.__expect_expression(
            self.__parse_identifier_or_function_call,
            PARSER_ERROR_TYPES.MISSING_EXPRESSION,
        )
        self.__expect_token_type(TokenType.T_SEMICOLON)
        return ThrowStatement(thrown_expression, position)

    def __parse_break_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_BREAK):
            return None
        self.__expect_token_type(TokenType.T_SEMICOLON)
        return BreakStatement(position)

    def __parse_continue_statement(self, position: Position) -> IStatement:
        if not self.__consume_if(TokenType.T_CONTINUE):
            return None
        self.__expect_token_type(TokenType.T_SEMICOLON)
        return ContinueStatement(position)

    def __parse_statement(self) -> IStatement:
        position = self.current_token.position
        return (
            self.__parse_if_statement(position)
            or self.__parse_while_statement(position)
            or self.__parse_return_statement(position)
            or self.__parse_for_statement(position)
            or self.__parse_variable_statement(position)
            or self.__parse_try_catch_statement(position)
            or self.__parse_throw_exception_statement(position)
            or self.__parse_break_statement(position)
            or self.__parse_continue_statement(position)
        )

    ############################## FUNCTION DEF ##############################

    def __parse_parameter(self):
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            return None
        name = self.current_token.value
        self.__next_token()
        if not self.__consume_if(TokenType.T_OPTIONAL):
            return Parameter(name)
        if not self.__consume_if(TokenType.T_ASSIGN):
            return Parameter(name, is_optional=True)
        token = self.current_token
        if constructor := literal_with_value_token_to_constructor.get(token.type):
            self.__next_token()
            return Parameter(
                name,
                is_optional=True,
                value=constructor(token.value),
            )
        elif constructor := literal_without_value_token_to_constructor.get(token.type):
            self.__next_token()
            return Parameter(
                name,
                is_optional=True,
                value=constructor(),
            )
        elif self.__check_token_type(TokenType.T_IDENTIFIER):
            self.__next_token()
            expression = self.__expect_expression(
                self.__parse_property_access_expression,
                PARSER_ERROR_TYPES.MISSING_EXPRESSION,
            )
            return Parameter(name, is_optional=True, value=expression)
        else:
            self.__add_error(PARSER_ERROR_TYPES.INVALID_PARAMETER_VALUE)

    def __check_if_param_is_valid(
        self, param: Parameter, parameters: list[Parameter]
    ) -> None:
        if param is None:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_PARAMETER)
        elif next((x for x in parameters if x.name == param.name), None) is not None:
            self.__add_error(PARSER_ERROR_TYPES.PARAMETER_ALREADY_EXIST)
        else:
            parameters.append(param)

    def __parse_parameters(self) -> list[Parameter]:
        parameters: list[Parameter] = []
        param = self.__parse_parameter()
        if param is None:
            return parameters
        self.__check_if_param_is_valid(param, parameters)
        while self.__consume_if(TokenType.T_COMMA):
            param = self.__parse_parameter()
            self.__check_if_param_is_valid(param, parameters)
        return parameters

    def __parse_func_def(self, functions: dict) -> bool:
        while self.__consume_if(TokenType.T_COMMENT):
            pass
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            return False
        name = self.current_token.value
        position = self.current_token.position
        self.__next_token()
        self.__expect_token_type(TokenType.T_LEFT_BRACKET)
        parameters = self.__parse_parameters()
        self.__expect_token_type(TokenType.T_RIGHT_BRACKET)
        block = self.__expect_block()
        if functions.get(name):
            self.__add_error(PARSER_ERROR_TYPES.FUNCTION_ALREADY_EXIST)
        functions[name] = FunctionDef(parameters, block, position)
        return True

    def parse(self) -> Program:
        functions: dict[str, FunctionDef] = {}
        while self.__parse_func_def(functions):
            pass
        return Program(functions)
