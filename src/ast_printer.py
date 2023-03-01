
# This module is for development and debugging purposes, printing a
# reasonable layout version of the input program.
# It is based on the visitors_base and AST modules that together implement
# the recursive traversal and visit functionality.


from visitors_base import VisitorsBase


class ASTTreePrinterVisitor(VisitorsBase):
    """The visitor implementing the pretty printing of the AST as a tree."""
    def __init__(self):
        self._node_number = 0
        self._text = []
        self._text.append("digraph G {\n")
        self._text.append("node[shape=box,width=0.1,height=0.1,margin=0.03]\n")

    def getPrettyProgram(self):
        return "".join(self._text).strip() + "\n}"

    def _node(self, s, n):
        self._text.append(f'{n}[label="{s}"]\n')

    def _edge(self, n_r, n_c):
        self._text.append(f'{n_r}->{n_c}\n')

    def _next(self):
        self._node_number += 1
        return self._node_number

    def postVisit_body(self, t):
        t.dotnum = self._next()
        self._node("body", t.dotnum)
        if t.variables_decl:
            self._edge(t.dotnum, t.variables_decl.dotnum)
        if t.functions_decl:
            self._edge(t.dotnum, t.functions_decl.dotnum)
        self._edge(t.dotnum, t.stm_list.dotnum)

    def postVisit_variables_declaration_list(self, t):
        t.dotnum = self._next()
        self._node("var_decl_list", t.dotnum)
        self._edge(t.dotnum, t.decl.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)

    def postVisit_functions_declaration_list(self, t):
        t.dotnum = self._next()
        self._node("func_decl_list", t.dotnum)
        self._edge(t.dotnum, t.decl.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)

    def postVisit_function(self, t):
        t.dotnum = self._next()
        self._node(f"function: {t.name}", t.dotnum)
        if t.par_list:
            self._edge(t.dotnum, t.par_list.dotnum)
        self._edge(t.dotnum, t.body.dotnum)

    def postVisit_parameter_list(self, t):
        t.dotnum = self._next()
        self._node(f"par_list: {t.parameter}", t.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)

    def postVisit_variables_list(self, t):
        t.dotnum = self._next()
        self._node(f"var_list: {t.variable}", t.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)

    def postVisit_statement_return(self, t):
        t.dotnum = self._next()
        self._node("return", t.dotnum)
        self._edge(t.dotnum, t.exp.dotnum)

    def postVisit_statement_print(self, t):
        t.dotnum = self._next()
        self._node("print", t.dotnum)
        self._edge(t.dotnum, t.exp.dotnum)

    def postVisit_statement_assignment(self, t):
        t.dotnum = self._next()
        self._node(f"assignment: {t.lhs}", t.dotnum)
        self._edge(t.dotnum, t.rhs.dotnum)

    def postVisit_statement_ifthenelse(self, t):
        t.dotnum = self._next()
        self._node("if_then_else", t.dotnum)
        self._edge(t.dotnum, t.exp.dotnum)
        self._edge(t.dotnum, t.then_part.dotnum)
        self._edge(t.dotnum, t.else_part.dotnum)

    def postVisit_statement_while(self, t):
        t.dotnum = self._next()
        self._node("while_do", t.dotnum)
        self._edge(t.dotnum, t.exp.dotnum)
        self._edge(t.dotnum, t.while_part.dotnum)

    def postVisit_statement_list(self, t):
        t.dotnum = self._next()
        self._node("stm_list", t.dotnum)
        self._edge(t.dotnum, t.stm.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)

    def postVisit_expression_integer(self, t):
        t.dotnum = self._next()
        self._node(f"int: {t.integer}", t.dotnum)

    def postVisit_expression_identifier(self, t):
        t.dotnum = self._next()
        self._node(f"id: {t.identifier}", t.dotnum)

    def postVisit_expression_call(self, t):
        t.dotnum = self._next()
        self._node(f"call: {t.name}", t.dotnum)
        if t.exp_list:
            self._edge(t.dotnum, t.exp_list.dotnum)

    def postVisit_expression_binop(self, t):
        t.dotnum = self._next()
        self._node(f"binop: {t.op}", t.dotnum)
        self._edge(t.dotnum, t.lhs.dotnum)
        self._edge(t.dotnum, t.rhs.dotnum)

    def postVisit_expression_list(self, t):
        t.dotnum = self._next()
        self._node("exp_list", t.dotnum)
        self._edge(t.dotnum, t.exp.dotnum)
        if t.next:
            self._edge(t.dotnum, t.next.dotnum)
