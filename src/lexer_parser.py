

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
    'IDENT', 'INT', 'BOOL', #Types
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
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'IDENT')
    return t

def t_COMMENT(t):
    r'\#.*'
    pass
