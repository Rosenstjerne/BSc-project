
# This module uses the ply module and is written according to the
# directions for that module. Thus, the programming style of this
# module deviates from the rest of the modules. This module uses the
# definitions from the module AST to build an abstract syntax tree.
# Interfacing with the next phase in the compiler is via the
# variables in the interfacing_parser module for storing the AST and
# a possible error message.


import ply.lex as lex
import ply.yacc as yacc

import interfacing_parser
import AST
from errors import error_message


# LEXICAL UNITS

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'function': 'FUNCTION',
    'return': 'RETURN',
    'var': 'VAR',
    'print': 'PRINT'
}


tokens = (
    'IDENT', 'INT',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LCURL', 'RCURL',
    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE',
    'ASSIGN', 'COMMA', 'SEMICOL',
) + tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_COMMA = r','
t_SEMICOL = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURL = r'{'
t_RCURL = r'}'
t_EQ = r'=='
t_NEQ = r'!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='


def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'IDENT')    # Check for reserved words
    return t


def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        error_message("Lexical Analysis",
                      f"Integer value too large.",
                      t.lexer.lineno)
        t.value = 0
    if t.value > int('0x7FFFFFFFFFFFFFFF', 16):
        error_message("Lexical Analysis",
                      f"Integer value too large.",
                      t.lexer.lineno)
        t.value = 0
    return t


# Ignored characters
t_ignore = " \t\r"  # \r included for the sake of windows users


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_COMMENT(t):
    r'\#.*'
    pass


def t_error(t):
    error_message("Lexical Analysis",
                  f"Illegal character '{t.value[0]}'.",
                  t.lexer.lineno)
    t.lexer.skip(1)


# PARSING RULES AND BUILDING THE AST

precedence = (
    ('right', 'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


# First production identifies the start symbol
def p_program(t):
    'program : body'
    interfacing_parser.the_program = AST.function("main", None, t[1], t.lexer.lineno)


def p_empty(t):
    'empty :'
    t[0] = None


def p_body(t):
    'body : optional_variables_declaration_list optional_functions_declaration_list statement_list'
    t[0] = AST.body(t[1], t[2], t[3], t.lexer.lineno)


def p_optional_variables_declaration_list(t):
    '''optional_variables_declaration_list : empty
                                           | variables_declaration_list'''
    t[0] = t[1]


def p_variables_declaration_list(t):
    '''variables_declaration_list : VAR variables_list
                                  | VAR variables_list variables_declaration_list'''
    if len(t) == 3:
        t[0] = AST.variables_declaration_list(t[2], None, t.lexer.lineno)
    else:
        t[0] = AST.variables_declaration_list(t[2], t[3], t.lexer.lineno)


def p_variables_list(t):
    '''variables_list : IDENT
                      | IDENT COMMA variables_list'''
    if len(t) == 2:
        t[0] = AST.variables_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.variables_list(t[1], t[3], t.lexer.lineno)


def p_optional_functions_declaration_list(t):
    '''optional_functions_declaration_list : empty
                                           | functions_declaration_list'''
    t[0] = t[1]


def p_functions_declaration_list(t):
    '''functions_declaration_list : function
                                  | function functions_declaration_list'''
    if len(t) == 2:
        t[0] = AST.functions_declaration_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.functions_declaration_list(t[1], t[2], t.lexer.lineno)


def p_function(t):
    'function : FUNCTION IDENT LPAREN optional_parameter_list RPAREN LCURL body RCURL'
    t[0] = AST.function(t[2], t[4], t[7], t.lexer.lineno)


def p_optional_parameter_list(t):
    '''optional_parameter_list : empty
                               | parameter_list'''
    t[0] = t[1]


def p_parameter_list(t):
    '''parameter_list : IDENT
                      | IDENT COMMA parameter_list'''
    if len(t) == 2:
        t[0] = AST.parameter_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.parameter_list(t[1], t[3], t.lexer.lineno)


def p_statement(t):
    '''statement : statement_return
                 | statement_print
                 | statement_assignment
                 | statement_ifthenelse
                 | statement_while
                 | statement_compound'''
    t[0] = t[1]


def p_statement_return(t):
    'statement_return : RETURN expression SEMICOL'
    t[0] = AST.statement_return(t[2], t.lexer.lineno)


def p_statement_print(t):
    'statement_print : PRINT expression SEMICOL'
    t[0] = AST.statement_print(t[2], t.lexer.lineno)


def p_statement_assignment(t):
    'statement_assignment : IDENT ASSIGN expression SEMICOL'
    t[0] = AST.statement_assignment(t[1], t[3], t.lexer.lineno)


def p_statement_ifthenelse(t):
    'statement_ifthenelse : IF expression THEN statement ELSE statement'
    t[0] = AST.statement_ifthenelse(t[2], t[4], t[6], t.lexer.lineno)


def p_statement_while(t):
    'statement_while :  WHILE expression DO statement'
    t[0] = AST.statement_while(t[2], t[4], t.lexer.lineno)


def p_statement_compound(t):
    'statement_compound :  LCURL statement_list RCURL'
    t[0] = t[2]


def p_statement_list(t):
    '''statement_list : statement
                      | statement statement_list'''
    if len(t) == 2:
        t[0] = AST.statement_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.statement_list(t[1], t[2], t.lexer.lineno)


def p_expression(t):
    '''expression : expression_integer
                  | expression_identifier
                  | expression_call
                  | expression_binop
                  | expression_group'''
    t[0] = t[1]


def p_expression_integer(t):
    'expression_integer : INT'
    t[0] = AST.expression_integer(t[1], t.lexer.lineno)


def p_expression_identifier(t):
    'expression_identifier : IDENT'
    t[0] = AST.expression_identifier(t[1], t.lexer.lineno)


def p_expression_call(t):
    'expression_call : IDENT LPAREN optional_expression_list RPAREN'
    t[0] = AST.expression_call(t[1], t[3], t.lexer.lineno)


def p_expression_binop(t):
    '''expression_binop : expression PLUS expression
                        | expression MINUS expression
                        | expression TIMES expression
                        | expression DIVIDE expression
                        | expression EQ expression
                        | expression NEQ expression
                        | expression LT expression
                        | expression GT expression
                        | expression LTE expression
                        | expression GTE expression'''
    t[0] = AST.expression_binop(t[2], t[1], t[3], t.lexer.lineno)


def p_expression_group(t):
    'expression_group : LPAREN expression RPAREN'
    t[0] = t[2]


def p_optional_expression_list(t):
    '''optional_expression_list : empty
                                | expression_list'''
    t[0] = t[1]


def p_expression_list(t):
    '''expression_list : expression
                       | expression COMMA expression_list'''
    if len(t) == 2:
        t[0] = AST.expression_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.expression_list(t[1], t[3], t.lexer.lineno)


def p_error(t):
    try:
        cause = f" at '{t.value}'"
        location = t.lexer.lineno
    except AttributeError:
        cause = " - check for missing closing braces"
        location = "unknown"
    error_message("Syntax Analysis",
                  f"Problem detected{cause}.",
                  location)


# Build the lexer
lexer = lex.lex()

# Build the parser
parser = yacc.yacc()
