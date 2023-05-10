from visitors_base import VisitorsBase


class ASTFunDecouple(VisitorsBase):
    def __init__(self):
        self.fun_tab = []

    def getFunctions(self):
        return self.fun_tab

    def postMidVisit_body(self, t):
        t.functions_decl = None

    def preVisit_function(self, t):
        self.fun_tab.append(t)
