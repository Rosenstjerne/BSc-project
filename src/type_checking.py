
from visitors_base import VisitorsBase
from errors import error_message
from symbols import NameCategory

# This module performs type checking. Since there is only one primitive
# type, integer, not much has to be done.
# It is based on the visitors_base and AST modules that together implement
# the recursive traversal and visit functionality.


class ASTTypeCheckingVisitor(VisitorsBase):
    def __init__(self):
        # The current scope in the form of a reference to the local
        # symbol table, from where parent scopes can be reached:
        self._current_scope = None
        # For computing the number of actual parameters to function calls,
        # a stack is necessary, since function calls can be nested. Pushes
        # and pops are executed at the entry to and exit from a function
        # call, and expressions in between those two points are counted:
        self.number_of_actual_parameters = []

    def preVisit_function(self, t):
        self._current_scope = t.symbol_table

    def postVisit_function(self, t):
        self._current_scope = self._current_scope.parent

    def postVisit_statement_assignment(self, t):
        value = self._current_scope.lookup(t.lhs)
        if not value:
            error_message("Symbol Collection",
                          f"Variable '{t.lhs}' not found.",
                          t.lineno)
        if value.cat == NameCategory.PARAMETER:
            error_message("Type Checking",
                          f"Assignment to parameter '{t.lhs}' not allowed.",
                          t.lineno)
        elif value.cat == NameCategory.FUNCTION:
            error_message("Type Checking",
                          f"Assignment to function '{t.lhs}' not allowed.",
                          t.lineno)

    def postVisit_expression_identifier(self, t):
        value = self._current_scope.lookup(t.identifier)
        if not value:
            error_message("Symbol Collection",
                          f"Identifier '{t.identifier}' not found.",
                          t.lineno)
        if value.cat == NameCategory.FUNCTION:
            error_message(
                "Type Checking",
                f"Function name '{t.identifier}' cannot be an identifier.",
                t.lineno)

    def preVisit_expression_call(self, t):
        self.number_of_actual_parameters.append(0)

    def postVisit_expression_call(self, t):
        value = self._current_scope.lookup(t.name)
        if not value:
            error_message("Symbol Collection",
                          f"Function '{t.name}' not found.",
                          t.lineno)
        elif value.cat != NameCategory.FUNCTION:
            error_message("Symbol Collection",
                          f"Identifier '{t.name}' is not a function.",
                          t.lineno)
        node = value.info
        if self.number_of_actual_parameters[-1] < node.number_of_parameters:
            error_message("Type Checking",
                          f"'{t.name}' was called with too few parameters.",
                          t.lineno)
        elif self.number_of_actual_parameters[-1] > node.number_of_parameters:
            error_message("Type Checking",
                          f"'{t.name}' was called with too many parameters.",
                          t.lineno)
        self.number_of_actual_parameters.pop()

    def midVisit_expression_list(self, t):
        self.number_of_actual_parameters[-1] += 1
