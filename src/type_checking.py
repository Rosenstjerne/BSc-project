
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

        self.current_function_stack = []
        self.while_nesting_stack = []

    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postVisit_body(self, t):
        self._current_scope = t.scope.parent

    def preVisit_function(self, t):
        if t.name != "main":
            self.current_function_stack.append(t)

    def postVisit_function(self, t):
        if t.name != "main":
            self.current_function_stack.pop()
    
    def preVisit_statement_list(self, t):
        if self._current_scope.is_function:
            if t.next is None:
                if self.current_function_stack[-1].rtype != "null":
                    if hasattr(t.stm, "legal"):
                        t.stm.legal = True
                    else:
                        error_message(
                                "Type Checking",
                                f"Function '{self.current_function_stack[-1].name}' is missing a return statement",
                                self._current_scope.name
                                )
                    
    def preVisit_statement_return(self, t):
        if t.legal:
            t._type = self.current_function_stack[-1].rtype
            t.function = self.current_function_stack[-1]
        else:
            error_message(
                    "Type Checking",
                    f"Illigaly places return statement",
                    t.lineno
                    )

    def postVisit_statement_return(self, t):
        if t._type == t.exp._type:
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Actual return type '{t._type}' does not match return type  of '{t.function.name}': '{t.function.rtype}'",
                    t.lineno
                    )


    def postVisit_statement_print(self, t): 
        if t.exp._type.replace("[]","") in ["int","bool"]:
            t.printType = t.exp._type
        else:
            error_message(
                    "Type Checking",
                    f"Not able to print values of type '{t.exp._type}'",
                    t.lineno
                    )

    def postVisit_statement_assignment(self, t):
        if t.lhs._type == t.rhs._type:
            t._type = t.lhs._type
        else:
            error_message(
                    "Type Checking",
                    f"Trying to assign a value of type '{t.rhs._type}' to a varaible of type '{t.lhs._type}' is not possible",
                    t.lineno
                    )

    def postVisit_variable(self, t):
        """saves its own type"""
        pass

    def postVisit_dot_variable(self, t):
        class_list = t.scope.atribute_lookup(t.elm)
        if t.exp._type in class_list:
            t.paren = class_list[t.exp._type]
            t._type = class_list[t.exp._type][t.elm].rtype
        else:
            error_message(
                    "Type Checking",
                    f"Type '{t.exp._type}' does not have an atribute '{t.elm}'",
                    t.lineno
                    )

    def postVisit_expression_index(self, t):
        if "[]" in t.exp._type:
            t._type = t.exp._type[:-2]
        else:
            error_message(
                    "Type Checking",
                    f"Can not index into type '{t.exp._type}'",
                    t.lineno
                    )
        if t.index._type == "int":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Type '{t.index._type}' can not be used to index into an array. Only allowed idexing type is 'int'",
                    t.lineno
                    )


    def postVisit_expression_new_array(self, t):
        if t.len._type == "int":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Type '{t.len._type}' can not be used to index into an array. Only allowed idexing type is 'int'",
                    t.lineno
                    )


    def midVisit_statement_ifthen(self, t):
        if t.exp._type == "bool":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"An expression of type '{t.exp._type}' cannot be used as a guarde. Must be of type 'bool'",
                    t.lineno
                    )

    def preMidVisit_statement_ifthenelse(self, t):
        if t.exp._type == "bool":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"An expression of type '{t.exp._type}' cannot be used as a guarde. Must be of type 'bool'",
                    t.lineno
                    )

    
    def midVisit_statement_while(self, t):
        if t.exp._type == "bool":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"An expression of type '{t.exp._type}' cannot be used as a guarde. Must be of type 'bool'",
                    t.lineno
                    )
        self.while_nesting_stack.append(t)
    
    def postVisit_statement_while(self, t):
        self.while_nesting_stack.pop()

    def postVisit_expression_negative(self, t):
        if t.exp._type == "int":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Can not take negative value of an expression of type '{t.exp._type}'. Must be of type 'int'",
                    t.lineno
                    )

    def postVisit_expression_neg(self, t):
        if t.exp._type == "bool":
            pass
        else:
            error_message(
                    "Type Checking",
                    f"Can not negate expression of '{t.exp._type}'. Must be of type 'bool'",
                    t.lineno
                    )

    def preVisit_expression_call(self, t):
        t.arg_lst = []
        if t.exp_list:
            t.exp_list.arg_lst = t.arg_lst

    def midVisit_expression_list(self, t):
        if t.next is not None:
            t.next.arg_lst = t.arg_lst
        t._type = t.exp._type
        t.arg_lst.append(t)

    def postVisit_expression_call(self, t):
        a = t.arg_lst
        p = t.function.parameter_list
        for i in range(t.number_of_parameters):
            if a[i]._type == p[i]._type:
                a[i].parameter = p[i]
            else:
                error_message(
                        "Type Checking",
                        f"Argument {i} in call to function {t.name} is of type '{a[i]._type}', but must be of type '{p[i]._type}'",
                        t.lineno
                        )

    def postVisit_expression_binop(self, t):
        if t.takes == "any":
            if t.lhs._type in ["int", "bool"]:
                if t.lhs._type == t.rhs._type:
                    pass
                else:
                    error_message("Type Checking", f"Both sides of the '{t.op}' operator must be same type", t.lineno)
            else:
                error_message("Type Checking", f"The '{t.op}' can only take types of 'int' or 'bool'. Found '{t.lhs._type}'", t.lineno)
        else:
            if (t.lhs._type == t.takes) and (t.rhs._type == t.takes):
                pass
            else:
                error_message(
                        "Type Checking",
                        f"Types '{t.lhs._type}' and '{t.rhs._type}' are not compatible with operator '{t.op}', which can only be used type '{t.takes}'",
                        t.lineno
                        )
    def postVisit_statement_break(self, t):
        if len(self.while_nesting_stack) > 0:
            t.parent = self.while_nesting_stack[-1]
        else:
            error_message("Type Checking",
                          f"Iligal break statement outside of any while loop",
                          t.lineno)
