
# This module provides class definitions for all the node types in the
# abstract syntax tree (AST). Each node accepts a visitor via its
# accept method, which implements a generic recursive traversal of
# the AST, calling preVisit, postVisit, and other visits at appropriate
# times, relative to the recursive traversals of the children. See
# the module visitors_base for how concrete visitors are dispatched.


class body:
    def __init__(self, class_list, variables_decl, functions_decl, stm_list, lineno):
        self.variables_decl = variables_decl
        self.functions_decl = functions_decl
        self.stm_list = stm_list
        self.class_list = class_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.variables_decl:
            self.variables_decl.accept(visitor)
        visitor.preMidVisit(self)
        if self.functions_decl:
            self.functions_decl.accept(visitor)
        visitor.postMidVisit(self)
        self.stm_list.accept(visitor)
        visitor.postVisit(self)

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

class class_declaration:
    def __init__(self, name, var_list, lineno):
        self.name = name
        self.var_list = var_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.var_list.accept(visitor)
        visitor.postVisit(self)

class variables_declaration_list:
    def __init__(self, vtype, decl, next_, lineno):
        self.vtype = vtype
        self.decl = decl
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.decl.accept(visitor)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)


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


class function:
    def __init__(self, name, par_list, body, lineno):
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


class parameter_list:
    def __init__(self, parameter, next_, lineno):
        self.parameter = parameter
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)


class variables_list:
    def __init__(self, variable, next_, lineno):
        self.variable = variable
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)


class statement_return:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)


class statement_print:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)


class statement_assignment:
    def __init__(self, lhs, rhs, lineno):
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)


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


class expression_integer:
    def __init__(self, i, lineno):
        self.integer = i
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)

class expression_boolean:
    def __init__(self, b, lineno):
        self.boolean = b
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)

class expression_neg:
    def __init__(self, exp, lineno):
        self.exp = exp
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.postVisit(self)

class expression_identifier:
    def __init__(self, identifier, lineno):
        self.identifier = identifier
        self.lineno = lineno

    def accept(self, visitor):
        visitor.postVisit(self)


class expression_call:
    def __init__(self, name, exp_list, lineno):
        self.name = name
        self.exp_list = exp_list
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        if self.exp_list:
            self.exp_list.accept(visitor)
        visitor.postVisit(self)


class expression_binop:
    def __init__(self, op, lhs, rhs, lineno):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.lhs.accept(visitor)
        visitor.midVisit(self)
        self.rhs.accept(visitor)
        visitor.postVisit(self)


class expression_list:
    def __init__(self, exp, next_, lineno):
        self.exp = exp
        self.next = next_
        self.lineno = lineno

    def accept(self, visitor):
        visitor.preVisit(self)
        self.exp.accept(visitor)
        visitor.midVisit(self)
        if self.next:
            self.next.accept(visitor)
        visitor.postVisit(self)
