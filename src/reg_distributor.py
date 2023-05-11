import itertools

from visitors_base import VisitorsBase

class intermediateRegister:
    def __init__(self, name):
        self.name = name
        self.firstUse = -1 # Based on line no
        self.lastUse = -1  # Based on line no
        self.color = None # For later use
        self.neighbours = [] # For later use
        self.regType = 0
        self.offset = 0

    def getReg(self):
        return self.color

    def use(self, lineno):
        if self.firstUse == -1:
            self.firstUse = lineno
        self.lastUse = lineno
        return self

    def setcolor(self, color):
        self.color = color

    def addNeighbour(self, *args):
        for n in args:
            self.neighbours.append(n)

    def addNeighboursConditionally(self, neighbours):
        for n in neighbours:
            if n.firstUse in range(self.firstUse,self.lastUse+1):
                self.neighbours.append(n)
            if n.lastUse in range(self.firstUse,self.lastUse+1):
                self.neighbours.append(n)
            if self.firstUse in range(n.firstUse,n.lastUse+1):
                self.neighbours.append(n)
            if self.lastUse in range(n.firstUse,n.lastUse+1):
                self.neighbours.append(n)



class ASTRegDistributor(VisitorsBase):
    def __init__(self, flatTab):
        self.counter = 0
        self.labelCounter = 0
        self._current_scope = None
        self.registers = []  # List of all intermediate registers
        self.chromatic_number = 0  # Number of actual registers we need to use in total
        self.flatTab = flatTab
        self.current_function_stack = []
        self.lineno = 1

    def getExterRegisterCount(self):
        return 0 if self.chromatic_number <= len(regMap) else self.chromatic_number - len(regMap)

    def colorRegisters(self):

        # Makes edges between concurently used registers
        for r in self.registers:
            r.addNeighboursConditionally(self.registers) 

        # Greedy algorithme for coloring the graph
        for r in self.registers:
            used_colors = {neighbour.color for neighbour in r.neighbours if neighbour.color is not None}
            min_available_color = next((c for c in itertools.count() if getRegName(c) not in used_colors), 0)
            colorReg(r,min_available_color)
            # r.setcolor(getRegName(min_available_color))
            if min_available_color + 1 > self.chromatic_number:
                self.chromatic_number = min_available_color + 1


    def newReg(self):
        name = f"reg{self.counter}"
        reg = intermediateRegister(name)
        self.registers.append(reg)
        self.counter += 1
        return reg

    def useReg(self, *args):
        for r in args:
            r.use(self.lineno)
        self.lineno += 1

    def newLbl(self, s=""):
        lbl = f"lbl{self.labelCounter}_{s}"        
        self.labelCounter += 1
        return lbl

    # Visitor functions

    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postVisit_body(self, t):
        if self._current_scope:
            self._current_scope = self._current_scope.parent

    def preVisit_function(self, t):
        self.current_function_stack.append(t.metaName)
        if t.name == "main":
            t.start_label = "main"
            t.end_label = "end_main"
        else:
            t.start_label = t.metaName
            t.end_label = f"end_{t.metaName}"

    def postVisit_function(self, t):
        self.current_function_stack.pop

    def postVisit_expression_list(self, t):
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_expression_call(self, t):
        t.call_label = t.function.start_label
        t.call_meta_function = t.function.metaName
        t.number_of_parameters = t.function.number_of_parameters
        t.retReg = self.newReg()
        self.useReg(t.retReg)

    def postVisit_expression_integer(self,t):
        t.retReg = self.newReg()
        self.useReg(t.retReg)
    
    def postVisit_expression_negative(self, t):
        t.inReg = t.exp.retReg
        t.retReg = self.newReg()
        self.useReg(t.inReg, t.retReg)

    def postVisit_expression_boolean(self, t):
        t.retReg = self.newReg()
        self.useReg(t.retReg)

    def postVisit_expression_neg(self, t):
        t.inReg = t.exp.retReg
        t.retReg = self.newReg()
        t.true_label = self.newLbl("exp_neg_true")
        t.end_label = self.newLbl("exp_neg_end")
        self.useReg(t.inReg)
        self.useReg(t.retReg)

    def postVisit_variable(self, t):
        if self._current_scope:
            t.metaVar = self._current_scope.lookup(t.name).metaVar 
        t.retReg = self.newReg() 
        self.useReg(t.retReg)

    def postVisit_expression_binop(self, t):
        t.inReg1 = t.lhs.retReg
        t.inReg2 = t.rhs.retReg
        t.retReg = self.newReg()
        self.useReg(t.inReg2, t.retReg)
        self.useReg(t.inReg1, t.retReg)

        if t.op in ["==","!=","<",">","<=",">="]:
            t.true_label = self.newLbl(f"cmp_true")
            t.end_label = self.newLbl(f"cmp_end")

    def postVisit_statement_print(self, t): 
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_assignment(self, t):
        t.inReg = t.rhs.retReg
        # t.assignReg = t.lhs.retReg
        self.useReg(t.inReg)

    def postVisit_statement_ifthen(self, t):
        t.end_label = self.newLbl("if_end")
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_ifthenelse(self, t):
        t.else_label = self.newLbl("if_else_else")
        t.end_label = self.newLbl("if_else_end")
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def midVisit_statement_while(self, t):
        t.begin_label = self.newLbl("while_begin")
        t.end_label = self.newLbl("while_end")
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_break(self, t):
        t.goto_label = t.parent.end_label

    def postVisit_expression_new(self, t):
        t.retReg = self.newReg()
        self.useReg(t.retReg)

    def postVisit_expression_new_array(self, t):
        t.retReg = self.newReg()
        t.sizeReg = t.len.retReg
        self.useReg(t.sizeReg, t.retReg)

    def postVisit_dot_variable(self, t):
        t.retReg = self.newReg()
        t.inReg = t.exp.retReg
        self.useReg(t.inReg, t.retReg)

    def postVisit_expression_index(self, t):
        t.retReg = self.newReg()
        t.inReg = t.exp.retReg
        t.indexReg = t.index.retReg
        self.useReg(t.inReg, t.indexReg, t.retReg)
    
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
        name = f"stackReg{i}" # TODO: What base should we use ?
        return name

def colorReg(r,n):
    r.setcolor(getRegName(n))
    if n not in regMap.keys():
        r.regType = 1
        i = n - len(regMap)
        r.offset = i 
