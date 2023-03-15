
# This module defines symbol tables and the symbol collection phase.
# It is based on the visitors_base and AST modules that together implement
# the recursive traversal and visit functionality.


from enum import Enum, auto

from errors import error_message
from visitors_base import VisitorsBase
import AST

class NameCategory(Enum):
    """Categories for the names (symbols) collected and inserted into
       the symbol table.
    """
    CLASS = auto()
    VARIABLE = auto()
    PARAMETER = auto()
    FUNCTION = auto()


class SymVal():
    """The information for a name (symbol) is its category together with
       supplementary information.
    """
    def __init__(self, cat, level, info, vtype):
        self.cat = cat
        self.level = level
        self.info = info
        self.rtype = vtype
        self.pClass = pClass


class SymbolTable:
    """Implements a classic symbol table for static nested scope.
       Names for each scope are collected in a Python dictionary.
       The parent scope can be accessed via the parent reference.
    """
    def __init__(self, parent, lineno):
        self._tab = {}
        self._types = {'int' : {}, 'bool' : {}}
        self.name = lineno
        self.parent = parent

    def insert(self, name, value):
        self._tab[name] = value

    def insert_type(self, typeName, att):
        self._types[typeName] = att

    def lookup(self, name):
        if name in self._tab:
            return self._tab[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None

    def lookup_this_scope(self, name):
        if name in self._tab:
            return self._tab[name]
        else:
            return None

    def type_lookup(self, name):
        if name in self._types:
            return self._types[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None

    def type_lookup_this_scope(self, name):
        if name in self._types:
            return self._types[name]
        else:
            return None

# Symbol Collection

class ASTSymbolVisitor(VisitorsBase):
    """The visitor implementing the symbol phase."""
    def __init__(self):
        # The main scope does not have a surrounding scope
        self._current_scope = SymbolTable(None, 0)
        # Have not entered the main scope (level 0) yet:
        self._current_level = 0

    def preVisit_body(self, t):
        # Parameters, classes, variables and functions belonge to the scope of the body:
        self._current_level += 1
        self._current_scope = SymbolTable(self._current_scope, t.lineno)
        if hasattr(t, 'function'):
            f = t.function

        # Preparing for processing local variables:
        self.variable_offset = 0
        

    def preMidVisit_body(self, t):
        pass

    def midVisit_body(self, t):
        # Recording the number of local variables:
        t.number_of_variables = self.variable_offset

        # Saving the current symbol table in the AST for future use:
        t.symbol_table = self._current_scope
        t.scope_level = self._current_level

    def postVisit_body(self, t):
        # Returning to the outer scope after function processing is completed:
        self._current_scope = self._current_scope.parent
        self._current_level -= 1

    def preVisit_function(self, t):
        # The name of the function belongs to the surrounding scope:
        if t.name != "main":
            if self._current_scope.lookup_this_scope(t.name):
                error_message(
                    "Symbol Collection",
                    f"Redeclaration of function '{t.name}' in the same scope.",
                    t.lineno)
            self._current_scope.insert(
                t.name, SymVal(NameCategory.FUNCTION, self._current_level, t, t.rtype))

        # Saves the function declaration to its body in the AST for later use
        t.body.function = t 
        
        # Preparing for the processing of formal parameters:
        self.parameter_offset = 0

    def midVisit_function(self, t):
        # Saving the number of formal parameters after the parameter
        # processing is completed:
        t.number_of_parameters = self.parameter_offset

    def postVisit_function(self, t):
        pass

    def preVisit_parameter_list(self, t):
        # Recording formal parameter names in the symbol table:
        if self._current_scope.lookup_this_scope(t.parameter):
            error_message(
                "Symbol Collection",
                f"Redeclaration of '{t.parameter}' in the same scope.",
                t.lineno)
        self._current_scope.insert(
            t.parameter, SymVal(NameCategory.PARAMETER,
                                self._current_level,
                                self.parameter_offset,
                                t.vtype))
        self.parameter_offset += 1

    def preVisit_variables_declaration_list(self, t):
        # propagates the type to the inner declarations for later use
        t.decl.vtype = t.vtype
        if hasattr(t, "parentClass"):
            t.decl.parentClass = t.parentClass
            if t.next:
                t.next.parentClass = t.parentClass

    def preVisit_variables_list(self, t):  # TODO: We need to know weather we are in a class or in a body. We also need to know the type
        # Recording local variable names in the symbol table:
        if self._current_scope.lookup_this_scope(t.variable):
            error_message(
                "Symbol Collection",
                f"Redeclaration of '{t.variable}' in the same scope.",
                t.lineno)

        # if the variable is part of a class declaration, dont add it to the symbol table 
        # but rather append it to a attibute list of the parent
        if hasattr(t, "attLst"):
            t.attLst.append(t)
            if t.next:
                t.next.attLst = t.attLst
        else:
            self._current_scope.insert(
                t.variable, SymVal(NameCategory.VARIABLE,
                                   self._current_level,
                                   self.variable_offset,
                                   t.vtype))
            self.variable_offset += 1

        # Hansd the variable type to the next varaible for later use
        if t.next:
            t.next.vtype = t.vtype

    def preVisit_class_declaration(self, t):
        # if a class with the same name is already declared in this scope, throw an error
        if self._current_scope.type_lookup_this_scope(t.name):
                error_message(
                    "Symbol Collection",
                    f"Redeclaration of class '{t.name}' in the same scope.",
                    t.lineno)

        # adds a 
        t.attLst = []
        t.var_list.attLst = t.attLst

    def postVisit_class_declaration(self, t):
        # creates a dictonary of all the internal attibutes of the class and saves it as the value of said class
       values = {(a.name):(SymVal(NameCategory.VARIABLE,self._current_level,None,a.vtype)) for a in t.attLst} 
       self._current_scope.insert_type(t.name, values)
