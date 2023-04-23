
from visitors_base import VisitorsBase

class intermediateRegister:
    def __init__(self, name):
        self.name = name
        self.firstUse = 0 # Based on line no
        self.lastUse = 0  # Based on line no
        self.collor = None # For later use
        self.neighbours = [] # For later use

    def getReg(self):
        return self.name

    def use(self, lineno):
        if self.firstUse == 0:
            self.firstUse = lineno
        self.lastUse = lineno

    def setCollor(self, collor):
        self.collor = collor

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

    def hasNeighbour(self, neighbour):
        return neighbour in self.neighbours

    def hasCollor(self, collor):
        return self.collor == collor

    def canHaveCollor(self, collor):
        for n in self.neighbours:
            if n.hasCollor(collor):
                return False
        return True


class regDistributor(VisitorsBase):
    def __init__(self, flatTab):
        self.counter = 0
        self.lableCounter = 0
        self._current_scope = None
        self.registers = []  # List of all intermediate registers
        self.cromaticNumber = 0  # Number of actual registers we need to use in total
        self.flatTab = flatTab
        self.current_function_stack = []
        self.pseudoLineno = 1

    def useReg(self, *args):
        for reg in args:
            reg.use()
        self.pseudoLineno += 1

    def addLine(self, n = 1):
        self.pseudoLineno += n

    def getExterRegisterCount(self):
        return 0 if self.cromaticNumber <= len(regMap) else self.cromaticNumber - len(regMap)

    def collorRegisters(self):

        # Makes edges between concurently used registers
        for r in self.registers:
            r.addNeighboursConditionally(self.registers) 

        # Collores all the registers in the graph
        for r in self.registers:
            c = 0
            while not r.canHaveCollor(getRegName(c)):
                c += 1 
            r.setCollor(getRegName(c))
            if c + 1 > self.cromaticNumber:
                self.cromaticNumber = c + 1


    def newReg(self):
        name = "reg_" + str(self.counter)
        reg = intermediateRegister(name)
        self.registers.append(reg)
        self.counter += 1
        self.useReg(reg)
        return reg

    def newLbl(self):
        lbl = "lable_" + str(self.lableCounter)
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
        self.useReg(t.inReg)
        t.retReg = self.newReg()

    def postVisit_variable(self, t):
        if self._current_scope:
            t.var = self._current_scope.lookup(t.name).var 
        t.retReg = t.var  # Should not return a ragister 

    def postVisit_expression_binop(self, t):
        t.inReg1 = t.lsh.retReg
        t.inReg2 = t.rsh.retReg
        self.useReg(t.inReg1, t.inReg2)
        t.retReg = self.newReg()

    def postVisit_statement_print(self, t): 
        t.inReg = t.exp.retReg
        self.useReg(t.inReg)

    def postVisit_statement_assignment(self, t):
        t.inReg = t.rhs.retReg
        self.useReg(t.inReg)
        t.assignReg = t.lhs.retReg  # Not a register

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
    if n in regMap.keys:
        return regMap[n]
    else:
        i = n - len(regMap) + 1
        name = "-" + str(i*8) + "RBX" # TODO: What base should we use ?
        return name
