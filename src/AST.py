
# This module should provide the necisarry code to create an abstract syntax tree

class body:
    def __init__(self, variables_decl, functions_decl, classes_delc, stm_list, lineno):
        self.variables_decl = variables_decl
        self.functions_decl = functions_decl
        self.classes_decl = classes_decl
        self.stm_list = stm_list
        self. lineno = lineno

    def accept(self, visiotor):
        visitor.preVisit(self)
        if self.variables_decl:
            self.variables_decl.accept(visitor)
        visitor.preMidVisit(self)
        if self.functions_decl:
            self.functions_decl.accept(visitor)
        visitor.postMidVisit(self)
        self.stm_list.accept(visitor)
        visitor.postVisit(self)


class variables_declaration_list:
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


class classes_declaration_list:
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

#TODO: Fill out the rest of the nodes
