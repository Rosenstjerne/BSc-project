

import ply.lex as lex
import ply.yacc as yacc

import interfacing_parser
import AST
from error import error_message

reserved = {
        'if': 'IF',
        'elif': 'ELIF',
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
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'IDENT')
    return t

def t_INT(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        error_message("Lexical analyser",f"Something went lexing the integer. Value to large.",t.lexer.lineno)
        t.value = 0
    if t.value > int('0x7FFFFFFFFFFFFFFF', 16):
        error_message("Lexical analyser",f"Something went lexing the integer. Value to large.",t.lexer.lineno)
        t.value = 0
    return t

def t_BOOL(t):
    r'(true)|(false)' #Cathes a few variations og the name
    try:
        t.value = bool(t.value)
    except ValueError:
        error_message("Lexical analyser",f"Something went lexing the boolean.",t.lexer.lineno)
        t.value = False
    return t

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
    error_message("Lexical analyser",f"Illigal character '{t.value[0]}'.",t.lexer.lineno)

# Ignored charecters
t_ignore = " \t\r"

# PARSING RULES AND BUILDING AST
#TODO: When the AST is finished: make the parsing rules


# Builds the lexer 
lexer = lex.lex()

# Builds the parser
parser = yacc.yacc()
