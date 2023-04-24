# This visitor is meant to "flatten" the symbol table, so that we don't have any nested functions any more
# This allows us to ignore all scopes 

from visitors_base import VisitorsBase
from symbols import NameCategory

class flatFun:
    def __init__(self, name, info, parentList):
        self.name = name
        self.info = info
        self.varCounter = 0
        self.paramCounter = 0
        self.parentList = []
        for i in range(len(parentList)):
            self.parentList.append(parentList[i])
        self.varTab = {}
        self.paramTab = {}

class variable:
    def __init__(self, name, scope, index):
        self.name = name
        self.scope = scope
        self.index = index


class ASTTabFlattener(VisitorsBase):
    def __init__(self):
        self._current_level = 0
        self.current_function_count = 0
        self.current_variable_count = 0
        self.current_function_stack = []
        self.var_table = {}

    def preVisit_body(self,t):
        scope = t.scope._tab
        for a in scope.keys():
            if scope[a].cat == NameCategory.VARIABLE:
                name = "var_" + str(self.current_variable_count) + "_" + a
                self.current_variable_count += 1
                metaName = [self.current_function_stack[-1], name]
                var = variable(metaName, self.current_function_stack[-1].name, self.current_function_stack[-1].varCounter)
                self.current_function_stack[-1].varCounter += 1
                scope[a].var = var
                self.var_table[self.current_function_stack[-1]].varTab[name] = var

            elif scope[a].cat == NameCategory.PARAMETER:
                name = "param_" + str(self.current_variable_count) + "_" + a
                self.current_variable_count += 1
                metaName = [self.current_function_stack[-1], name]
                param = variable(metaName, self.current_function_stack[-1].name, self.current_function_stack[-1].paramCounter)
                self.current_function_stack[-1].paramCounter += 1
                scope[a].var = param
                self.var_table[self.current_function_stack[-1]].paramTab[name] = param

    def preVisit_function(self, t):
        self.current_function_count += 1
        name = "fun_" + str(self.current_function_count) + "_" + t.name
        funFlatTab = flatFun(name, t.scope, self.current_function_stack)
        self.var_table[name] = funFlatTab
        self.current_function_stack.append(name)
        t.metaName = name

    def postVisit_function(self, t):
        self.current_function_stack.pop
