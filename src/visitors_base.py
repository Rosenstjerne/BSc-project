
# This module provides the base class for all the visitors. The purpose
# is to allow the implementer of the subsequent phases in the compiler
# to write code only for the parts of the AST where the given phase
# has to take action.


class VisitorsBase:

    def _visit(self, t, s):
        method = getattr(self, s + "_" + t.__class__.__name__, None)
        if method:
            method(t)

    def preVisit(self, t):
        self._visit(t, "preVisit")

    def preMidVisit(self, t):
        self._visit(t, "preMidVisit")

    def midVisit(self, t):
        self._visit(t, "midVisit")

    def postMidVisit(self, t):
        self._visit(t, "postMidVisit")

    def postVisit(self, t):
        self._visit(t, "postVisit")
