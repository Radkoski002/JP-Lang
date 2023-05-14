from lexer.lexer_class import Lexer
from program.program_class import Program
from parser.statement_classes import *
from lexer.token_class import Token
from lexer.token_type_enum import TokenType
from parser.helpers import INFIX_EXPRESSIONS, token_to_constructor
from parser.parser_error_class import PARSER_ERROR_TYPES, ParserError


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.error_handler = lexer.error_handler
        self.current_token: Token = lexer.build_next_token()

        self.infix_expression_params: dict[INFIX_EXPRESSIONS] = {
            INFIX_EXPRESSIONS.OR: self.__create_infix_expression_param(
                self.__parse_and_expression, [TokenType.T_OR]
            ),
            INFIX_EXPRESSIONS.AND: self.__create_infix_expression_param(
                self.__parse_comparation_expression,
                [TokenType.T_AND],
            ),
            INFIX_EXPRESSIONS.COMPARISON: self.__create_infix_expression_param(
                self.__parse_addition_expression,
                [
                    TokenType.T_EQUAL,
                    TokenType.T_NOT_EQUAL,
                    TokenType.T_LESS,
                    TokenType.T_LESS_EQUAL,
                    TokenType.T_GREATER,
                    TokenType.T_GREATER_EQUAL,
                ],
            ),
            INFIX_EXPRESSIONS.ADDITION: self.__create_infix_expression_param(
                self.__parse_multiplication_expression,
                [TokenType.T_PLUS, TokenType.T_MINUS],
            ),
            INFIX_EXPRESSIONS.MULTIPLICATION: self.__create_infix_expression_param(
                self.__parse_negation_expression,
                [TokenType.T_MULTIPLY, TokenType.T_DIVIDE, TokenType.T_MODULO],
            ),
            INFIX_EXPRESSIONS.PROPERTY_ACCESS: self.__create_infix_expression_param(
                self.__parse_identifier_or_function_call,
                [TokenType.T_ACCESS, TokenType.T_NULLABLE_ACCESS],
            ),
        }

    ############################## UTILS ##############################

    @staticmethod
    def __create_infix_expression_param(function, token: list[TokenType]) -> dict:
        return {
            "function": function,
            "token": token,
        }

    def __add_error(self, error_type: PARSER_ERROR_TYPES) -> None:
        self.error_handler.add_error(
            ParserError(error_type, self.current_token.position)
        )

    def __check_token_type(self, token_type: TokenType) -> bool:
        return self.current_token.type == token_type

    def __check_if_token_type_in_list(self, token_types: list[TokenType]) -> bool:
        return self.current_token.type in token_types

    def __consume_if(self, token_type: TokenType) -> bool:
        if self.__check_token_type(token_type):
            self.__next_token()
            return True
        return False

    def __consume_if_in_list(self, token_types: list[TokenType]) -> bool:
        if self.__check_if_token_type_in_list(token_types):
            self.__next_token()
            return True
        return False

    def __consume_if_and_return_token(self, token_type: TokenType) -> Token:
        token = self.current_token
        if self.__consume_if(token_type):
            return token
        return None

    def __consume_if_in_list_and_return_token(
        self, token_types: list[TokenType]
    ) -> Token:
        token = self.current_token
        if self.__consume_if_in_list(token_types):
            return token
        return None

    def __next_token(self) -> None:
        self.current_token = self.lexer.build_next_token()

    ############################## EXPRESSIONS ##############################

    def __parse_infix_expression(
        self, expression_type: INFIX_EXPRESSIONS
    ) -> IExpression:
        func_params = self.infix_expression_params[expression_type]
        left = func_params["function"]()
        if not left:
            return None
        while token := self.__consume_if_in_list_and_return_token(func_params["token"]):
            right = func_params["function"]()
            if not right:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_EXPRESSION)
            left = token_to_constructor[token.type](left, right)
        return left

    def __parse_property_access_expression(self) -> IExpression:
        return self.__parse_infix_expression(INFIX_EXPRESSIONS.PROPERTY_ACCESS)

    def __parse_arguments(self) -> list[IExpression]:
        is_reference = self.__consume_if(TokenType.T_REF)
        argument = self.__parse_expression()
        if not argument:
            return []
        arguments = [Argument(argument, is_reference)]
        while self.__consume_if(TokenType.T_COMMA):
            is_reference = self.__consume_if(TokenType.T_REF)
            argument = self.__parse_expression()
            if not argument:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_ARGUMENT)
            arguments.append(Argument(argument, is_reference))
        return arguments

    def __parse_rest_of_function_call(self, name: str) -> IExpression:
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            return None
        arguments = self.__parse_arguments()
        if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        return FunctionCallExpression(name, arguments)

    def __parse_identifier_or_function_call(self) -> IExpression:
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            return None

        name = self.current_token.value
        self.__next_token()

        expression = self.__parse_rest_of_function_call(name)
        if not expression:
            return IdentifierExpression(name)
        return expression

    def __parse_expression_in_brackets(self) -> IExpression:
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            return None
        expression = self.__parse_expression()
        if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        return expression

    def __parse_primary_expression(self):
        if self.__check_if_token_type_in_list(
            [
                TokenType.T_INT_LITERAL,
                TokenType.T_FLOAT_LITERAL,
                TokenType.T_STRING_LITERAL,
            ]
        ):
            expression = token_to_constructor[self.current_token.type](
                self.current_token.value
            )
            self.__next_token()
        elif self.__check_token_type(TokenType.T_IDENTIFIER):
            expression = self.__parse_property_access_expression()
        elif self.__check_if_token_type_in_list(
            [
                TokenType.T_NULL,
                TokenType.T_TRUE,
                TokenType.T_FALSE,
            ]
        ):
            expression = token_to_constructor[self.current_token.type]()
            self.__next_token()
        else:
            expression = self.__parse_expression_in_brackets()
        return expression

    def __parse_type_check_expression(self) -> IExpression:
        expression = self.__parse_primary_expression()
        if not expression:
            return None
        if not self.__consume_if(TokenType.T_TYPE_CHECK):
            return expression
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_TYPE_NAME)
        type_name = IdentifierExpression(self.current_token.value)
        self.__next_token()
        return TypeCheckExpression(expression, type_name)

    def __parse_negation_expression(self) -> IExpression:
        if token := self.__consume_if_in_list_and_return_token(
            [TokenType.T_NOT, TokenType.T_MINUS]
        ):
            expression = self.__parse_expression()
            if not expression:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_EXPRESSION)
            if token.type == TokenType.T_MINUS:
                return NumericNegationExpression(expression)
            if token.type == TokenType.T_NOT:
                return BitwiseNegationExpression(expression)
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
        if not self.__consume_if(TokenType.T_LEFT_CURLY_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_BLOCK_START)
        statements: list[IStatement] = []
        while statement := self.__parse_statement():
            if statement is None:
                break
            statements.append(statement)
        if not self.__consume_if(TokenType.T_RIGHT_CURLY_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_BLOCK_END)
        return BlockStatement(statements)

    def __parse_condition(self) -> IExpression:
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET)
        condition = self.__parse_expression()
        if not condition:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION)
        if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        return condition

    def __parse_if_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_IF):
            return None
        elif_statements: list[BlockStatement] = []
        else_statement: BlockStatement = None
        condition = self.__parse_condition()
        statement = self.__parse_block_statement()
        if not condition:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION)
        while self.__consume_if(TokenType.T_ELIF):
            elif_condition = self.__parse_condition()
            elif_statement = self.__parse_block_statement()
            if not elif_condition:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION)
            elif_statements.append(ConditionalStatement(elif_condition, elif_statement))
        if self.__consume_if(TokenType.T_ELSE):
            else_statement = self.__parse_block_statement()
        return IfStatement(condition, statement, elif_statements, else_statement)

    def __parse_while_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_WHILE):
            return None
        condition = self.__parse_condition()
        statement = self.__parse_block_statement()
        if not condition:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CONDITIONAL_EXPRESSION)
        return WhileStatement(condition, statement)

    def __parse_for_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_FOR):
            return None
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET)
        variable_name = self.__parse_property_access_expression()
        if not variable_name:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_FOR_LOOP_VARIABLE)
        if not self.__consume_if(TokenType.T_COLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_FOR_LOOP_COLON)
        iterable = self.__parse_property_access_expression()
        if not iterable:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_FOR_LOOP_ITERABLE)
        if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        statement = self.__parse_block_statement()
        return ForStatement(variable_name, iterable, statement)

    def __parse_return_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_RETURN):
            return None
        expression = self.__parse_expression()
        if not self.__consume_if(TokenType.T_SEMICOLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
        return ReturnStatement(expression)

    def __parse_variable_statement(self) -> IStatement:
        identifier_or_fun_call = self.__parse_property_access_expression()
        if not identifier_or_fun_call:
            return None
        if type(identifier_or_fun_call) in [
            IdentifierExpression,
            PropertyAccessExpression,
        ] and self.__check_if_token_type_in_list(
            [
                TokenType.T_ASSIGN,
                TokenType.T_ASSIGN_PLUS,
                TokenType.T_ASSIGN_MINUS,
                TokenType.T_ASSIGN_MULTIPLY,
                TokenType.T_ASSIGN_DIVIDE,
                TokenType.T_ASSIGN_MODULO,
            ]
        ):
            operation_type = self.current_token.type
            self.__next_token()
            expression = self.__parse_expression()
            if not expression:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_EXPRESSION)
            if not self.__consume_if(TokenType.T_SEMICOLON):
                self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
            return token_to_constructor[operation_type](
                identifier_or_fun_call, expression
            )
        if not self.__consume_if(TokenType.T_SEMICOLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
        return identifier_or_fun_call

    def __parse_try_catch_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_TRY):
            return None
        try_statement = self.__parse_block_statement()
        if not self.__consume_if(TokenType.T_CATCH):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CATCH_KEYWORD)
        exception_types: list[IdentifierExpression] = []
        variable_name: IdentifierExpression = None
        if self.__consume_if(TokenType.T_LEFT_BRACKET):
            exception_type = self.__parse_identifier_or_function_call()
            if exception_type is None:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_ERROR_TYPE)
            exception_types = [exception_type]
            while self.__consume_if(TokenType.T_OR):
                error_type = self.__parse_identifier_or_function_call()
                if error_type is None:
                    self.__add_error(PARSER_ERROR_TYPES.MISSING_ERROR_TYPE)
                exception_types.append(error_type)
            variable_name = self.__parse_identifier_or_function_call()
            if variable_name is None:
                self.__add_error(PARSER_ERROR_TYPES.MISSING_ERROR_VARIABLE)
            if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
                self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        catch_statement = self.__parse_block_statement()
        return TryCatchStatement(
            try_statement, catch_statement, exception_types, variable_name
        )

    def __parse_throw_exception_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_THROW):
            return None
        thrown_expression = self.__parse_identifier_or_function_call()
        if not thrown_expression:
            self.__add_error(PARSER_ERROR_TYPES.MISSING_EXPRESSION)
        if not self.__consume_if(TokenType.T_SEMICOLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
        return ThrowStatement(thrown_expression)

    def __parse_break_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_BREAK):
            return None
        if not self.__consume_if(TokenType.T_SEMICOLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
        return BreakStatement()

    def __parse_continue_statement(self) -> IStatement:
        if not self.__consume_if(TokenType.T_CONTINUE):
            return None
        if not self.__consume_if(TokenType.T_SEMICOLON):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_SEMICOLON)
        return ContinueStatement()

    def __parse_comment(self) -> IStatement:
        if token := self.__consume_if_and_return_token(TokenType.T_COMMENT):
            return Comment(token.value)
        return None

    def __parse_statement(self) -> IStatement:
        return (
            self.__parse_if_statement()
            or self.__parse_while_statement()
            or self.__parse_return_statement()
            or self.__parse_for_statement()
            or self.__parse_variable_statement()
            or self.__parse_try_catch_statement()
            or self.__parse_throw_exception_statement()
            or self.__parse_break_statement()
            or self.__parse_continue_statement()
            or self.__parse_comment()
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
        if self.__check_if_token_type_in_list(
            [
                TokenType.T_STRING_LITERAL,
                TokenType.T_INT_LITERAL,
                TokenType.T_FLOAT_LITERAL,
            ]
        ):
            self.__next_token()
            return Parameter(
                name,
                is_optional=True,
                value=token_to_constructor[token.type](token.value),
            )
        elif self.__check_if_token_type_in_list(
            [
                TokenType.T_TRUE,
                TokenType.T_FALSE,
                TokenType.T_NULL,
            ]
        ):
            self.__next_token()
            return Parameter(
                name,
                is_optional=True,
                value=token_to_constructor[token.type](),
            )
        elif self.__check_token_type(TokenType.T_IDENTIFIER):
            self.__next_token()
            expression = self.__parse_property_access_expression()
            if expression is None:
                self.__add_error(PARSER_ERROR_TYPES.INVALID_PARAMETER_VALUE)
            return Parameter(name, is_optional=True, value=expression)
        else:
            self.__add_error(PARSER_ERROR_TYPES.INVALID_PARAMETER_VALUE)

    def __check_if_param_is_valid(
        self, param: Parameter, parameters: list[Parameter]
    ) -> None:
        if param is None:
            return
        elif next((x for x in parameters if x.name == param.name), None) is not None:
            return
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

    def __parse_func_def(self, functions) -> bool:
        if not self.__check_token_type(TokenType.T_IDENTIFIER):
            return False
        name = self.current_token.value
        self.__next_token()
        if not self.__consume_if(TokenType.T_LEFT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_OPENING_BRACKET)
        parameters = self.__parse_parameters()
        if not self.__consume_if(TokenType.T_RIGHT_BRACKET):
            self.__add_error(PARSER_ERROR_TYPES.MISSING_CLOSING_BRACKET)
        block = self.__parse_block_statement()
        functions[name] = FunctionDef(parameters, block)
        return True

    def parse(self) -> Program:
        functions: dict[str, FunctionDef] = {}
        while self.__parse_func_def(functions):
            pass
        return Program(functions)
