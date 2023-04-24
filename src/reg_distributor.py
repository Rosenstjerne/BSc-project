import itertools

from visitors_base import VisitorsBase

class intermediateRegister:
    def __init__(self, name):
        self.name = name
        self.firstUse = 0 # Based on line no
        self.lastUse = 0  # Based on line no
        self.color = None # For later use
        self.neighbours = [] # For later use

    def getReg(self):
        return self.color

    def use(self, lineno):
        if self.firstUse == 0:
            self.firstUse = lineno
        self.lastUse = lineno

    def setcolor(self, color):
        self.color = color

    def addNeighbour(self, *args):
        for n in args:
            self.neighbours.append(n)

    def addNeighboursConditionally(self, neighbours):
        for n in neighbours:
            if self == n:
                pass
            elif n.firstUse in range(self.firstUse, self.lastUse+1):
                self.neighbours.append(n)
            elif n.lastUse in range(self.firstUse, self.lastUse+1):
                self.neighbours.append(n)



class ASTRegDistributor(VisitorsBase):
    def __init__(self, flatTab):
        self.counter = 0
        self.lableCounter = 0
        self._current_scope = None
        self.registers = []  # List of all intermediate registers
        self.chromatic_number = 0  # Number of actual registers we need to use in total
        self.flatTab = flatTab
        self.current_function_stack = []
        self.pseudoLineno = 1

    def useReg(self, *args):
        for reg in args:
            reg.use(self.pseudoLineno)
        self.pseudoLineno += 1

    def addLine(self, n = 1):
        self.pseudoLineno += n

    def getExterRegisterCount(self):
        return 0 if self.chromatic_number <= len(regMap) else self.chromatic_number - len(regMap)

    def colorRegisters(self):

        # Makes edges between concurently used registers
        for r in self.registers:
            r.addNeighboursConditionally(self.registers) 

        # Greedy algorithme for coloring the graph
        for r in self.registers:
            used_colors = {neighbour.color for neighbour in r.neighbours if neighbour.color is not None}
            min_available_color = next((c for c in itertools.count() if getRegName(c) not in used_colors), -1)
            r.setcolor(getRegName(min_available_color))
            if min_available_color + 1 > self.chromatic_number:
                self.chromatic_number = min_available_color + 1


    def newReg(self):
        name = f"reg_{self.counter}"
        reg = intermediateRegister(name)
        self.registers.append(reg)
        self.counter += 1
        self.useReg(reg)
        return reg

    def newLbl(self):
        lbl = f"label_{self.label_counter}"
        self.lableCounter+= 1
        return lbl

    # Visitor functions

    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postVisit_body(self, t):
        if self._current_scope:
            self._current_scope = self._current_scope.parent

    def preVisit_function(self, t):
        self.current_function_stack.append(t.metaName)
        t.start_label = t.metaName
        t.end_label = f"end_{t.name}"

    def postVisit_function(self, t):
        self.current_function_stack.pop

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
        self.useReg(t.inReg)

    def postVisit_variable(self, t):
        if self._current_scope:
            t.var = self._current_scope.lookup(t.name).var 
        t.retReg = t.var  # Should not return a ragister 

    def postVisit_expression_binop(self, t):
        t.inReg1 = t.lhs.retReg
        t.inReg2 = t.rhs.retReg
        t.retReg = self.newReg()
        self.useReg(t.inReg1, t.inReg2)

    def postVisit_statement_print(self, t): 
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_assignment(self, t):
        t.inReg = t.rhs.retReg
        t.assignReg = t.lhs.retReg  # Not a register
        self.useReg(t.inReg)

    def postVisit_statement_ifthen(self, t):
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_ifthenelse(self, t):
        t.else_lbl = self.newLbl()
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_while(self, t):
        t.begin_lbl = self.newLbl()
        t.end_lbl = self.newLbl()
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_break(self, t):
        t.goto_lbl = t.parent.end_lbl

    def postVisit_expression_new(self, t):
        t.retReg = self.newReg()
        t.size = None # TODO : Figure out where the size is stored or how to calculate it

    def postVisit_expression_new_array(self, t):
        t.retReg = self.newReg()
        t.sizeReg = t.exp.retReg
        self.useReg(t.sizeReg)

    def postVisit_expression_call(self, t):  # TODO: Should we have this here? 
        pass

    def postVisit_dot_variable(self, t):
        t.retReg = self.newReg()
        t.inReg = t.exp.retRet
        self.useReg(t.inReg)

    def postVisit_expression_index(self, t):
        t.retReg = self.newReg()
        t.inReg = t.exp.retReg
        t.indexReg = t.index.retReg
        self.useReg(t.inReg, t.indexReg)
    
    def postVisit_statement_return(self, t):
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

# end of visitor

regMap = {
        0: "%r8",
        1: "%r9",
        2: "%r10",
        3: "%r11",
        4: "%r12",
        5: "%r13",
        6: "%r14",
        7: "%r15"
        }

def getRegName(n):
    if n in regMap.keys():
        return regMap[n]
    else:
        i = n - len(regMap) + 1
        name = f"-{i*8}(%rbx)" # TODO: What base should we use ?
        return name
