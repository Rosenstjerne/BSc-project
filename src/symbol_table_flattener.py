# This visitor is meant to "flatten" the symbol table, so that we don't have any nested functions any more
# This allows us to ignore all scopes 

from visitors_base import VisitorsBase

class flatTab:
    def __init__(self, name, info):
        self.name = name
        self.info = info
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
        self.var_table[name] = flatTab(name, t.scope)
        t.metaName = name

    def postVisit_function(self, t):
        self.current_function_stack.pop
