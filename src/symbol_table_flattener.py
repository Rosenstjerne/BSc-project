# This visitor is meant to "flatten" the symbol table, so that we don't have any nested functions any more
# This allows us to ignore all scopes 

from visitors_base import VisitorsBase

class flatFun:
    def __init__(self, name, info, parentList):
        self.name = name
        self.info = info
        self.parentList = []
        for i in range(len(parentList)):
            self.parentList.append(parentList[i])
        self.tab = {}


class tabFlattener(VisitorsBase):
    def __init__(self):
        self._current_level = 0
        self.current_function_count = 0
        self.current_variable_count = 0
        self.current_function_stack = []
        self.var_table = {}

    def preVisit_body(self,t):
        scope = t.scope._tab
        for a in scope.keys:
            name = "var" + str(self.current_variable_count) + a
            metaName = [self.current_function_stack[-1], name]
            scope[a].metaName = metaName
            self.var_table[self.current_function_stack[-1]].tab[name] = scope[a]

    def preVisit_function(self, t):
        self.current_function_count += 1
        name = "fun" + str(self.current_function_count) + t.name
        self.current_function_stack.append(name)
        self.var_table[name] = flatFun(name, t.scope, self.current_function_stack)
        t.metaName = name

    def postVisit_function(self, t):
        self.current_function_stack.pop
