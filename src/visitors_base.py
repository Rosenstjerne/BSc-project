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
