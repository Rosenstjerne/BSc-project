
from visitors_base import VisitorsBase

class regDistributor(VisitorsBase):
    def __init__(self):
        self.counter = 0
        self.lableCounter = 0
        self._current_scope = None

    def newReg(self):
        reg = "reg_" + str(self.counter)
        self.counter += 1
        return reg

    def newLbl(self):
        lbl = "lable_" + str(self.lableCounter)
        self.lableCounter+= 1
        return lbl

    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postVisit_body(self, t):
        if self._current_scope:
            self._current_scope = self._current_scope.parent

    def postVisit_expression_integer(self,t):
        t.retReg = self.newReg()
    
    def postVistit_exression_negative(self, t):
        t.inReg = t.ext.retReg
        t.retReg = self.newReg()

    def postVisit_expression_boolean(self, t):
        t.retReg = self.newReg()

    def postVistit_exression_neg(self, t):
        t.inReg = t.ext.retReg
        t.retReg = self.newReg()

    def postVisit_variable(self, t):
        if self._current_scope:
            t.var = self._current_scope.lookup(t.name).var 
        t.retReg = self.newReg()

    def postVisit_expression_binop(self, t):
        t.inReg1 = t.lsh.retReg
        t.inReg2 = t.rsh.retReg
        t.retReg = self.newReg()

    def postVisit_statement_print(self, t): 
        t.inReg = t.exp.retReg

    def postVisit_statement_assignment(self, t):
        t.inReg = t.rhs.retReg
        t.assignReg = t.lhs.retReg

    def postVisit_statement_ifthen(self, t):
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg

    def postVisit_statement_ifthenelse(self, t):
        t.else_lbl = self.newLbl()
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg

    def postVisit_statement_while(self, t):
        t.begin_lbl = self.newLbl()
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg

    def postVisit_statement_break(self, t):
        t.goto_lbl = t.parent.end_lbl

    def postVisit_expression_new(self, t):
        pass

    def postVisit_expression_new_array(self, t):
        pass

    def postVisit_expression_call(self, t):
        pass

    def postVisit_dot_variable(self, t):
        pass

    def postVisit_expression_index(self, t):
        pass
    
    def postVisit_statement_return(self, t):
        pass
