
# This module provides class definitions for all the node types in the
# abstract syntax tree (AST). Each node accepts a visitor via its
# accept method, which implements a generic recursive traversal of
# the AST, calling preVisit, postVisit, and other visits at appropriate
# times, relative to the recursive traversals of the children. See
# the module visitors_base for how concrete visitors are dispatched.

simpleTypes = {'int','bool'}

class body:
    def __init__(self, class_decl, variables_decl, functions_decl, stm_list, lineno):
        self.class_decl = class_decl
        self.variables_decl = variables_decl
        self.functions_decl = functions_decl
        self.stm_list = stm_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.class_decl:
            self.class_decl.accept(visitor)
        visitor.preMidVisit(self)
        if self.variables_decl:
            self.variables_decl.accept(visitor)
        visitor.midVisit(self)
        if self.functions_decl:
            self.functions_decl.accept(visitor)
        visitor.postMidVisit(self)
        self.stm_list.accept(visitor)
        visitor.postVisit(self)

    def __str__(self):
        s = ""
        if self.class_decl:
            s += toStr(self.class_decl) + "\n"
        if self.variables_decl:
            s += toStr(self.variables_decl) + "\n"
        if self.functions_decl:
            s += toStr(self.functions_decl) + "\n"
        s += toStr(self.stm_list)
        return s


class class_declaration_list:
    def __init__(self, decl, next_, lineno):
        self.decl = decl
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.decl.accept(visitor)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self):
        s = ""
        s += toStr(self.decl) + "\n"
        s += toStr(self.next)
        return s


class class_declaration:
    def __init__(self, name, var_list, lineno):
        self.name = name
        self.var_list = var_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.var_list.accept(visitor)
        visitor.postVisit(self)

    def __str__(self):
        s = "class "
        s += toStr(self.name) + " {\n"
        s += indent(toStr(self.var_list))
        s += "}"
        return s


class variables_declaration_list:
    def __init__(self, vtype, decl, next_, lineno):
        self.vtype = vtype
        self.decl = decl
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.decl.accept(visitor)
        visitor.midVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self):
        s = "var " + self.vtype + " "
        s += toStr(self.decl) + ";\n"
        if self.next:
            s += toStr(self.next)
        return s


class functions_declaration_list:
    def __init__(self, decl, next_, lineno):
        self.decl = decl
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.decl.accept(visitor)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.decl) + "\n"
        s += toStr(self.next)
        return s


class function:
    def __init__(self, rtype, name, par_list, body, lineno):
        self.rtype = rtype
        self.name = name
        self.par_list = par_list
        self.body = body
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.par_list:
            self.par_list.accept(visitor)
        visitor.midVisit(self)
        self.body.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "function " + toStr(self.rtype) + " " + toStr(self.name) + "(" + toStr(self.par_list) + ") {\n"
        s += indent(toStr(self.body))
        s += "\n}"
        return s


class parameter_list:
    def __init__(self, vtype, parameter, next_, lineno):
        self.vtype = vtype
        self.parameter = parameter
        self.next = next_
        self.lineno = lineno
        self._type = vtype # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.vtype) + " "
        s += toStr(self.parameter)
        if self.next:
            s += ", " + toStr(self.next)
        return s

class variables_list:
    def __init__(self, variable, next_, lineno):
        self.variable = variable
        self.next = next_
        self.lineno = lineno
        self._type = "" # for later check

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.variable)
        if self.next:
            s += ", " + toStr(self.next)
        return s


class statement_return:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno
        self.legal = False # for later check
        self._type = "unknown" # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "return "
        s += toStr(self.exp) + ";"
        return s


class statement_print:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno
        self.printType = "unknown" # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "print("
        s += toStr(self.exp) + ");"
        return s


class statement_assignment:
    def __init__(self, lhs, rhs, lineno):
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno
        self._type = "unknown" # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        self.lhs.accept(visitor)
        visitor.midVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.lhs) + " = " + toStr(self.rhs) + ";"
        return s


class statement_ifthen:
    def __init__(self, exp, then_part, lineno):
        self.exp = exp
        self.then_part = then_part
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.midVisit(self)
        self.then_part.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "if(" + toStr(self.exp) + ")\n"
        s += "#begin if\n"
        s += indent(toStr(self.then_part)) + "\n"
        s += "#end if"
        return s


class statement_ifthenelse:
    def __init__(self, exp, then_part, else_part, lineno):
        self.exp = exp
        self.then_part = then_part
        self.else_part = else_part
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.preMidVisit(self)
        self.then_part.accept(visitor)
        visitor.postMidVisit(self)
        self.else_part.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "if(" + toStr(self.exp) + ")\n"
        s += "#bein if\n"
        s += indent(toStr(self.then_part)) + "\n"
        s += "#end if\n#begin else\n"       
        s += "else\n"
        s += indent(toStr(self.else_part)) + "\n"
        s += "#end else"
        return s


class statement_while:
    def __init__(self, exp, while_part, lineno):
        self.exp = exp
        self.while_part = while_part
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.midVisit(self)
        self.while_part.accept(visitor)
        visitor.postVisit(self)


    def __str__(self) -> str:
        s = "while(" + toStr(self.exp) + ") {\n#begin while\n"
        s += indent(toStr(self.while_part)) + "\n}\n"
        s += "#end while\n"
        return s

class statement_break:
    def __init__(self, lineno):
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "break;"
        return s

class statement_list:
    def __init__(self, stm, next_, lineno):
        self.stm = stm
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.stm.accept(visitor)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.stm) + "\n"
        s += toStr(self.next)
        return s


class expression_integer:
    def __init__(self, i, lineno):
        self.integer = i
        self.lineno = lineno
        self._type = "int"

    def accept(self, visitor):
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.integer)
        return s

class expression_negative:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno
        self._type = "int"

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "(-" + toStr(self.exp) + ")"
        return s


class expression_boolean:
    def __init__(self, b, lineno):
        self.boolean = b
        self.lineno = lineno
        self._type = "bool"

    def accept(self, visitor):
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.boolean)
        return s


class expression_neg:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno
        self._type = "bool"

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "(! " + toStr(self.exp) + ")"
        return s



class expression_index:
    def __init__(self, exp, index, lineno):
        self.exp = exp
        self.index = index
        self.lineno = lineno
        self._type = "unknown" # for later use
        self.assign = False # for later use
        self.varType = "index_variable"

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        self.index.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "("
        s += toStr(self.exp) + "[" + toStr(self.index) + "])"
        return s

class variable:
    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
        self._type = "unknown" # for later use
        self.assign = False # for later use
        self.varType = "variable"

    def accept(self, visitor):
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = self.name
        return s

class dot_variable:
    def __init__(self, exp, elm, lineno):
        self.exp = exp
        self.elm = elm 
        self.lineno = lineno
        self._type = "unknown" # for later use
        self.assign = False # for later use
        self.varType = "dot_variable"

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "("
        s += toStr(self.exp) + "." + toStr(self.elm) + ")"
        return s

class expression_call:
    def __init__(self, name, exp_list, lineno):
        self.name = name
        self.exp_list = exp_list
        self.lineno = lineno
        self._type = "unknown" # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.exp_list:
            self.exp_list.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.name) + "(" + toStr(self.exp_list) + ")"
        return s


class expression_binop:
    def __init__(self, op, lhs, rhs, lineno):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno
        self.takes = ""
        self._type = ""
        if op in ["+","-","*","/","%"]:
            self.takes = "int"
            self._type = "int"
        if op in ["<","<=",">",">="]:
            self.takes = "int"
            self._type = "bool"
        if op in ["&&","||"]:
            self.takes = "bool"
            self._type = "bool"
        if op in ["==","!="]:
            self.takes = "any"
            self._type = "bool"


    def accept(self, visitor):
        visitor.preVisit(self)
        self.lhs.accept(visitor)
        visitor.midVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "("
        s += toStr(self.lhs) + " " + toStr(self.op) + " " + toStr(self.rhs)
        s += ")"
        return s


class expression_new:
    def __init__(self, r_type, lineno):
        self.r_type = r_type
        self.lineno = lineno
        self._type = r_type

    def accept(self, visitor):
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "(new " + toStr(self.r_type) + ")"
        return s

class expression_new_array:
    def __init__(self, i_type, len, lineno):
        self.e_type = i_type + "[]"
        self.i_type = i_type
        self.root_type = i_type.replace("[]","")
        self.len = len
        self.lineno = lineno
        self._type = self.e_type

    def accept(self, visitor):
        visitor.preVisit(self)
        self.len.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = "(new " + self.i_type + "["
        s += toStr(self.len) + "])"
        return s



class expression_list:
    def __init__(self, exp, next_, lineno):
        self.exp = exp
        self.next = next_
        self.lineno = lineno
        self._type = "unknown" # for later use

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.midVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)

    def __str__(self) -> str:
        s = ""
        s += toStr(self.exp)
        if self.next:
            s += ", " + toStr(self.next)
        return s

def indent(s, i : int = 1) -> str:
    if s:
        return "\t" * i + str(s).replace("\n","\n" + "\t" * i)
    else:
        return ""

def toStr(node):
    if node is not None:
        return str(node)
    else:
        return ""
