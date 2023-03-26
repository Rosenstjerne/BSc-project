
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

        self.current_function_name_stack = []
        self.function_return_stack = []
        self.while_nesting_stack = []

    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postVisit_body(self, t):
        self._current_scope = t.scope.parent

    def preVisit_function(self, t):
        if t.name != "main":
            self.function_return_stack.append(t.rtype)
            self.current_function_name_stack.append(t.name)

    def postVisit_function(self, t):
        if t.name != "main":
            self.function_return_stack.pop
            self.current_function_name_stack.pop
    
    def preVisit_statement_list(self, t):
        if self._current_scope.is_function:
            if t.next is None:
                if self.function_return_stack[-1] != "null":
                    if type(t.stm) == "statement_return":
                        t.stm.legal = True
                    else:
                        error_message(
                                "Type Checking",
                                f"Function '{self.current_function_name_stack[-1]}' is missing a return statement",
                                self._current_scope.name
                                )
                    
    def preVisit_statement_return(self, t):
        if t.legal:
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Illigaly places return statement",
                    t.lineno
                    )

    def postVisit_statement_return(self, t):
        
        """If the return type of the function is not compatible with the 
        return type of the expression in this return statemt, throw an error"""

        pass

    def postVisit_statement_print(self, t): 
        
        """If the return type of the expression is not bool, int or rootvalue bool / int 
        throw an error"""

        pass

    def postVisit_statement_assignment(self, t):
        """return an error if the lhs and the rhs types are not compatible"""
        pass

    def postVisit_variable(self, t):
        """saves its own type"""
        pass

    def postVisit_dot_variable(self, t):
        """Checks if its expression type has the given attribute
        Then saves it type"""
        pass

    def postVisit_expression_index(self, t):
        """Checks if the expression returns an array, then saves it type as the given arrays type, unpacked once"""
        pass

    def midVisit_statement_ifthen(self, t):
        """Checks it the guarde is a bool"""
        pass

    def preMidVisit_statement_ifthenelse(self, t):
        """Checks it the guarde is a bool"""
        pass

    
    def midVisit_statement_while(self, t):
        """Checks it the guarde is a bool"""
        self.while_nesting_stack.append(t)
    
    def postVisit_statement_while(self, t):
        self.while_nesting_stack.pop()

    def postVisit_expression_negative(self, t):
        """Throws an error if the expression is not int"""
        pass

    def postVisit_expression_neg(self, t):
        """Throws an error if the expression is not bool"""
        pass

    def preVisit_expression_call(self, t):
        t.arg_lst = []
        if t.exp_list:
            t.exp_list.arg_lst = t.arg_lst

    def postVisit_expression_call(self, t):
        """Checks if the argsuments given are compatible with the needed parameters for a function
        Saves a link between each argument to the respective parameter"""
        pass

    def postVisit_expression_binop(self, t):
        """
            - + : børnene skal være int. Returnere en int 
            - - : børnene skal være int. Returnere en int 
            - / : børnene skal være int. Returnere en int
            - * : børnene skal være int. Returnere en int
            - % : børnene skal være int. Returnere en int
            - ==: børnene skal være samme type. Returnere en bool
            - !=: børnene skal være samme type. Returnere en bool
            - < : børnene skal være int. Returnere en bool
            - > : børnene skal være int. Returnere en bool
            - <=: børnene skal være int. Returnere en bool
            - >=: børnene skal være int. Returnere en bool
            - &&: børnene skal være bool. Returnere en bool
            - ||: børnene skal være bool. Returnere en bool
        """
        pass

    
