
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
    'else': 'ELSE',
    'while': 'WHILE',
    'function': 'FUNCTION',
    'var': 'VAR',
    'break': 'BREAK',
    'print': 'PRINT',
    'class': 'CLASS',
    'return': 'RETURN',
    'new': 'NEW'
}


tokens = (
    'IDENT', 'INT', 'BOOL', 'ARRAY', #Types
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', # arithmatic int operators
    'EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE', # comparisons
    'AND', 'OR', 'NOT', # bool operators
    'LPAREN', 'RPAREN', 'LCURL', 'RCURL', 'LBRAC', 'RBRAC', # parenthesis / brackets
    'ASSIGN', 'COMMA', 'SEMICOLON', 'DOT' # other
) + tuple(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_ASSIGN = r'='
t_COMMA = r','
t_DOT = r'\.'
t_SEMICOLON = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LCURL = r'{'
t_RCURL = r'}'
t_LBRAC = r'\['
t_RBRAC = r'\]'
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
    if t.value > int('0x7FFFFFFFFFFFFFFF', 16):
        error_message("Lexical Analysis",
                      f"Integer value too large.",
                      t.lexer.lineno)
    return t

def t_BOOL(t):
    r'(true)|(false)' #Cathes a few variations og the name
    try:
        t.value = bool(t.value)
    except ValueError:
        error_message("Lexical analyser",f"Something went lexing the boolean.",t.lexer.lineno)
    return t


# Ignored characters
t_ignore = " \t\r"  # \r included for the sake of windows users


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_COMMENT(t):
    r'\#.*'
    pass

def t_COMMENTBLOCK(t):
    r'\#\*([a-zA-Z0-9_\n\ \*]|(\#\*))*\*\#' #Doesn't work with nested comment blocks. Works like comment blocks in C buth with # in stead of /
    t.lexer.loneno += t.value.count("\n") #Might take up some lines, so we need to keep track of them


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
    ('right', 'MODULO'),
    ('nonassoc', 'OR'),
    ('nonassoc', 'AND')
)


# First production identifies the start symbol
def p_program(t):
    'program : body'
    interfacing_parser.the_program = AST.function("main", None, t[1], t.lexer.lineno)


def p_empty(t):
    'empty :'
    t[0] = None


def p_body(t):
    'body : optional_class_declaration_list optional_variables_declaration_list optional_functions_declaration_list statement_list'
    t[0] = AST.body(t[1], t[2], t[3], t[4], t.lexer.lineno)

def p_optional_class_declaration_list(t):
    '''optional_class_declaration_list : empty
                                       | class_declaration_list'''
    t[0] = t[1]

def p_class_declaration_list(t):
    '''class_declaration_list : class_declaration
                              | class_declaration class_declaration_list'''
    if len(t) == 2:
        t[0] = AST.class_declaration_list(t[1], None, t.lexer.lineno)
    else:
        t[0] = AST.class_declaration_list(t[1], t[2], t.lexer.lineno)

def p_class_declaration(t):
    '''class_declaration : CLASS IDENT LCURL variables_declaration_list RCURL'''
    t[0] = AST.class_declaration(t[2], t[4], t.lexer.lineno)

def p_optional_variables_declaration_list(t):
    '''optional_variables_declaration_list : empty
                                           | variables_declaration_list'''
    t[0] = t[1]


def p_int_variables_declaration_list(t):
    '''variables_declaration_list : VAR variable_type variables_list
                                  | VAR variable_type variables_list variables_declaration_list'''
    if len(t) == 4:
        t[0] = AST.variables_declaration_list(t[2], t[3], None, t.lexer.lineno)
    else:
        t[0] = AST.variables_declaration_list(t[2], t[3], t[4], t.lexer.lineno)

def p_variable_type(t):
    '''variable_type : BOOL
                     | INT
                     | IDENT
                     | variable_type LBRAC RBRAC'''
    if len(t) == 4:
        t[0] = t[1] + t[2] + t[3]
    else:
        t[0] = t[1]

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
                 | statement_ifthen
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


def p_statement_ifthen(t):
    'statement_ifthen : IF LPAREN expression RPAREN statement'
    t[0] = AST.statement_ifthen(t[3], t[5], t.lexer.lineno)


def p_statement_ifthenelse(t):
    'statement_ifthenelse : IF LPAREN expression RPAREN statement ELSE statement'
    t[0] = AST.statement_ifthenelse(t[3], t[5], t[7], t.lexer.lineno)


def p_statement_while(t):
    'statement_while :  WHILE LPAREN expression RPAREN statement'
    t[0] = AST.statement_while(t[3], t[5], t.lexer.lineno)


def p_statement_compound(t):
    'statement_compound :  LCURL body RCURL'
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
                  | expression_boolean
                  | expression_identifier
                  | expression_call
                  | expression_binop
                  | expression_group
                  | expression_neg'''
    t[0] = t[1]


def p_expression_integer(t):
    'expression_integer : INT'
    t[0] = AST.expression_integer(t[1], t.lexer.lineno) 

def p_expression_boolean(t):
    'expression_boolean : BOOL'
    t[0] = AST.expression_boolean(t[1], t.lexer.lineno) 

def p_expression_neg(t):
    'expression_neg : NOT expression'
    t[0] = AST.expression_neg(t[2], t.lexer.lineno)

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
                        | expression GTE expression
                        | expression AND expression
                        | expression OR expression'''
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