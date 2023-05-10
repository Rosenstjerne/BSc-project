# This visitor is meant to "flatten" the symbol table, so that we don't have any nested functions any more
# This allows us to ignore all scopes 

from visitors_base import VisitorsBase
from symbols import NameCategory

class flatFun:
    def __init__(self, name, info, parentList):
        self.name = name
        self.info = info
        self.varCount = 0
        self.paramCount = 0
        self.parentList = []
        for i in range(len(parentList)):
            self.parentList.append(parentList[i])
        self.varTab = {}
        self.paramTab = {}

    def getStaticLinkClimb(self, elm):
        if elm.scope == self.name:
            return 0
        i = 0
        while i < len(self.parentList):
            if self.parentList[i].name == elm.scope:
                return len(self.parentList) - i
            i += 1
        return None

    def getStaticLinkFunClimb(self, fun_name):
        if fun_name == self.name:
            return 0
        i = 0
        while i < len(self.parentList):
            if self.parentList[i].name == fun_name:
                return len(self.parentList) - i - 1
            i += 1
        return -1


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
                metaName = [self.current_function_stack[-1].name, name]
                var = variable(metaName, self.current_function_stack[-1].name, self.current_function_stack[-1].varCount)
                self.current_function_stack[-1].varCount += 1
                scope[a].metaVar = var
                self.current_function_stack[-1].varTab[name] = var

            elif scope[a].cat == NameCategory.PARAMETER:
                name = "param_" + str(self.current_variable_count) + "_" + a
                self.current_variable_count += 1
                metaName = [self.current_function_stack[-1].name, name]
                param = variable(metaName, self.current_function_stack[-1].name, self.current_function_stack[-1].paramCount)
                self.current_function_stack[-1].paramCount += 1
                scope[a].metaVar = param
                self.current_function_stack[-1].paramTab[name] = param

    def preVisit_function(self, t):
        self.current_function_count += 1
        name = "fun_" + str(self.current_function_count) + "_" + t.name
        funFlatTab = flatFun(name, t.scope, self.current_function_stack)
        self.var_table[name] = funFlatTab
        self.current_function_stack.append(funFlatTab)
        t.flatFun = funFlatTab
        t.metaName = name

    def postVisit_function(self, t):
        self.current_function_stack.pop
