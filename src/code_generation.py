
# This module performs the compilation from an abstract syntax tree to
# an intermediate representation close to linear 64 bit x86 code. See the
# documentation for a definition of the intermediate representation.
# It is based on the visitors_base and AST modules that together implement
# the recursive traversal and visit functionality.

from enum import Enum, auto

from visitors_base import VisitorsBase
from symbols import NameCategory


class Operation(Enum):
    """Defines the various operations."""
    MOVE = auto()
    PUSH = auto()
    POP = auto()
    CALL = auto()
    RET = auto()
    CMP = auto()
    JMP = auto()
    JE = auto()
    JNE = auto()
    JL = auto()
    JLE = auto()
    JG = auto()
    JGE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    AND = auto()
    OR = auto()
    SHL = auto()
    LABEL = auto()
    META = auto()


class TargetType(Enum):
    """Defines an enumeration type for instruction argument targets. """
    IMI = auto()  # immediate integer
    IMB = auto()  # immediate boolean
    IML = auto()  # immediate label
    MEM = auto()  # memory (a label)
    RBP = auto()  # register: base (frame) pointer
    RSP = auto()  # register: stack pointer
    RRT = auto()  # register: return value
    RSL = auto()  # register: static link computation
    RBX = auto()  # register: intermediate values stack pointer
    RCX = auto()  # register: for intermediate use only
    REG = auto()  # general-purpose registers


class AddressingMode(Enum):
    """Defines an enumeration type for addressing modes. """
    DIR = auto()  # direct
    IND = auto()  # indirect
    IRL = auto()  # indirect relative
    IRR = auto()  # indirect relative by register


class Target:
    """Specification of a target, using class Type, and an optional argument."""
    def __init__(self, spec, *args):
        self.spec = spec
        if args:
            self.val = args[0]


class Mode:
    """Specification of an addressing mode, using class AddressingMode, and an optional
       argument.
    """
    def __init__(self, mode, *args):
        self.mode = mode
        if args:
            self.offset = args[0]


class Arg:
    """Representation of instruction arguments with a target and a mode."""
    def __init__(self, target, addressing):
        self.target = target
        self.addressing = addressing

class Ins:
    """Representation of an instruction with an opcode, a number of
       arguments, and an optional comment.
    """
    def __init__(self, *args, c=""):
        self.opcode = args[0]
        self.args = args[1:]
        self.comment = c

class Meta(Enum):
    PROGRAM_PROLOGUE = auto()
    PROGRAM_EPILOGUE = auto()
    MAIN_CALLEE_SAVE = auto()
    MAIN_CALLEE_RESTORE = auto()
    CALLEE_PROLOGUE = auto()
    CALLEE_EPILOGUE = auto()
    CALLEE_SAVE = auto()
    CALLEE_RESTORE = auto()
    CALLER_PROLOGUE = auto()
    CALLER_EPILOGUE = auto()
    CALLER_SAVE = auto()
    CALLER_RESTORE = auto()
    CALL_PRINTF = auto()
    ALLOCATE_STACK_SPACE = auto()
    DEALLOCATE_STACK_SPACE = auto()
    REVERSE_PUSH_ARGUMENTS = auto()
    ALLOCATE_HEAP_SPACE = auto()  # For Classes and Arrays

# Code generation

class ASTCodeGenerationVisitor(VisitorsBase):
    """Implements the intermediate code generation from the AST."""
    def __init__(self, flatTab):
        # The current scope in the form of a reference to the local
        # symbol table, from where parent scopes can be reached:
        self._current_scope = None
        # A stack of references to the definitions of functions in the
        # AST, representing the current nesting of scopes:
        self._function_stack = []
        # The code is collected in a list:
        self._code = []

        self.flatTab = flatTab
        self.lineno = 1

    
    def get_code(self):
        return self._code

    def _app(self, instruction):
        self._code.append(instruction)
        self.lineno = self.lineno + 1

    
    def _follow_static_link(self, level_difference):
        """Generates code to follow static link; at the end, rsl will
           point to rbp in the correct frame.
        """
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.RBP), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RSL), Mode(AddressingMode.DIR)),
                      c="preparing for static link computation"))
        for i in range(level_difference):
            # Static link is offset two from base pointer:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -2)),  # The parent base pointer
                          Arg(Target(TargetType.RSL), Mode(AddressingMode.DIR)),
                          c="following the static link"))


    # Visitor functions
    
    def preVisit_body(self, t):
        self._current_scope = t.scope

    def postMidVisit_body(self, t):
        pass

    def postVisit_body(self, t):
        if self._current_scope is not None:
            self._current_scope = self._current_scope.parent


    def preVisit_function(self, t):
        self._function_stack.append(t)

        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.start_label), Mode(AddressingMode.DIR))))
        self._app(Ins(Operation.META, Meta.CALLEE_PROLOGUE))
        self._app(Ins(Operation.META,
                      Meta.ALLOCATE_STACK_SPACE,
                      self.flatTab[t.metaName].varCount))
        if len(self._function_stack) == 1:
            # In the body of main:
            self._app(Ins(Operation.META, Meta.MAIN_CALLEE_SAVE))
        else:
            # In the body of a function:
            self._app(Ins(Operation.META, Meta.CALLEE_SAVE))


    def postVisit_function(self, t):
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR))))
        if len(self._function_stack) == 1:
            # In the body of main:
            self._app(Ins(Operation.META, Meta.MAIN_CALLEE_RESTORE))
        else:
            # In the body of a function:
            self._app(Ins(Operation.META, Meta.CALLEE_RESTORE))
        self._app(Ins(Operation.META, Meta.CALLEE_EPILOGUE))

        self._function_stack.pop()

    def preVisit_expression_call(self, t):
        self._app(Ins(Operation.META, Meta.CALLER_SAVE))
        self._app(Ins(Operation.META, Meta.CALLER_PROLOGUE))

    def postVisit_expression_list(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.PUSH,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          c="push arguement to stack"
                          )) 
        else:
            self._app(Ins(Operation.PUSH,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          c="push arguement to stack"
                          )) 

    def postVisit_expression_call(self, t):
        level_difference = self.flatTab[self._function_stack[-1].metaName].getStaticLinkFunClimb(t.call_meta_function)
        if level_difference == -1:
            # Calling inwards, i.e., a local function:
            self._app(Ins(Operation.PUSH, Arg(Target(TargetType.RBP), Mode(AddressingMode.DIR)),
                      c="set up static link for inner function"))
        else:
            # Calling outwards, i.e., same or outer level:
            self._follow_static_link(level_difference)
            self._app(Ins(Operation.PUSH,
                      Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -2)),
                      c="set up static link for outer function"))

        self._app(Ins(Operation.CALL,
                      Arg(Target(TargetType.MEM, t.call_label), Mode(AddressingMode.DIR))))

        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                      c=f"Moves the return value from %rax into {t.retReg.name}"
                      ))
        for i in range(t.number_of_parameters):
            self._app(Ins(Operation.POP,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c="Pops argument from stack"
                          ))

        self._app(Ins(Operation.META, Meta.CALLER_EPILOGUE))
        self._app(Ins(Operation.META, Meta.CALLER_RESTORE))




    def postVisit_statement_return(self, t):
        # Getting the function label from the nearest enclosing function:
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for return"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for return"))


    def postVisit_statement_print(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rcx for print"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for print"))

        self._app(Ins(Operation.META, 
                      Meta.CALL_PRINTF,
                      Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                      t.printType))

    
    def postVisit_expression_integer(self, t):
        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMI, t.integer), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves integer into {t.retReg.name}"))
        else: 
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMI, t.integer), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves integer into {t.retReg.name}"))
        
    def postVisit_expression_boolean(self, t):
        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMB, t.boolean), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves boolean into {t.retReg.name}"))
        else: 
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMB, t.boolean), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves integer into {t.retReg.name}"))


    def postVisit_variables_list(self, t):
        if hasattr(t, "attLst"):
            pass
        else:
            var = t.var.metaVar
            offset = var.index
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMI, 0), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBP), Mode(AddressingMode.IRL, offset + 1)),
                          c=f"Initializes {t.variable} to 0"))

    def postVisit_variable(self, t):
        if t.assign:
            pass
        else:
            var = t.metaVar
            level_difference = self.flatTab[self._function_stack[-1].metaName].getStaticLinkClimb(var)
            self._follow_static_link(level_difference)
            offset = var.index
            if t.var.cat == NameCategory.PARAMETER:
                if t.retReg.regType == 0:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -(offset + 3))),
                                  Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                                  c=f"Move param {var.name[1]} ({t.name}) into {t.retReg.name}"))
                else:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -(offset + 3))),
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR))))
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                                  c=f"Move param {var.name[1]} ({t.name}) into {t.retReg.name}"))
            elif t.var.cat == NameCategory.VARIABLE:
                if t.retReg.regType == 0:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, offset + 1)),
                                  Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                                  c=f"Move param {var.name[1]} ({t.name}) into {t.retReg.name}"))
                else:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, offset + 1)),
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR))))
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                                  c=f"Move param {var.name[1]} ({t.name}) into {t.retReg.name}"))
        
    def postVisit_statement_assignment(self, t):
        if t.lhs.varType == "variable":
            var = t.lhs.metaVar
            level_difference = self.flatTab[self._function_stack[-1].metaName].getStaticLinkClimb(var)
            self._follow_static_link(level_difference)
            offset = var.index
            if t.lhs.var.cat == NameCategory.PARAMETER:
                if t.rhs.retReg.regType == 0:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.REG, t.rhs.retReg), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -(offset + 3))),
                                  c=f"Move param {t.rhs.retReg.name} into {var.name} ({t.lhs.name})"))
                else:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.rhs.retReg.offset)),
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR))))
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, -(offset + 3))),
                                  c=f"Move param {t.rhs.retReg.name} into {var.name} ({t.lhs.name})"))
            elif t.lhs.var.cat == NameCategory.VARIABLE:
                if t.rhs.retReg.regType == 0:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.REG, t.rhs.retReg), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, offset + 1)),
                                  c=f"Move param {t.rhs.retReg.name} into {var.name} ({t.lhs.name})"))
                else:
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.rhs.retReg.offset)),
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR))))
                    self._app(Ins(Operation.MOVE,
                                  Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                                  Arg(Target(TargetType.RSL), Mode(AddressingMode.IRL, offset + 1)),
                                  c=f"Move param {t.rhs.retReg.name} into {var.name} ({t.lhs.name})"))
        if t.lhs.varType == "dot_variable":
            if t.inReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for insert"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for insert"))
        
            if t.lhs.retReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.lhs.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.inReg.name} for indexing"))
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.IRL, -t.lhs.index)),
                              c=f"Moves {t.inReg.name} into the dot variable"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.lhs.inReg.offset)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.inReg.name} for indexing"))
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.IRL, -t.lhs.index)),
                              c=f"Moves {t.inReg.name} into the dot variable"))

        if t.lhs.varType == "index_variable":
            if t.inReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RSL), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for insert"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                              Arg(Target(TargetType.RSL), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for insert"))


            if t.lhs.indexReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.lhs.indexReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.indexReg.name} out for indexing in"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.lhs.indexReg.offset)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.indexReg.name} out for indexing in"))

        
            if t.lhs.retReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.lhs.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.inReg.name} for indexing"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.lhs.inReg.offset)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.lhs.inReg.name} for indexing"))


            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RSL), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.IRR)),
                          c=f"Moves {t.inReg.name} into the dot variable"))


    def postVisit_expression_new(self, t):
        self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.IMI, t.alloc_size), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves size out into %rcx for allication"))

        self._app(Ins(Operation.META, 
                      Meta.ALLOCATE_HEAP_SPACE,
                      c=f"allocates memory"))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves new array into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves new array into {t.retReg.name}"))


    def postVisit_dot_variable(self, t):
        if t.assign:
            pass
        else:
            if t.inReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for indexing"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for indexing"))

            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.IRL, -t.index)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c="Gets the dot variable into %rax"))

            if t.retReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                              c=f"Moves new array into {t.retReg.name}"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                              c=f"Moves new array into {t.retReg.name}"))

    def postVisit_expression_new_array(self, t):
        if t.sizeReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.sizeReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.sizeReg.name} out into %rcx for allication size"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.sizeReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.sizeReg.name} out of the stack for allocation size"))

        self._app(Ins(Operation.META, 
                      Meta.ALLOCATE_HEAP_SPACE,
                      c=f"allocates memory"))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves new array into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves new array into {t.retReg.name}"))

    def postVisit_expression_index(self, t):
        if t.assign:
            pass
        else:
            if t.inReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.indexReg.name} out for indexing in"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.inReg.name} out for indexing in"))

            if t.indexReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.REG, t.indexReg), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.indexReg.name} out for indexing in"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.indexReg.offset)),
                              Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                              c=f"Moves {t.indexReg.name} out for indexing in"))

            # self._app(Ins(Operation.SHL,
            #               Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
            #               Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
            #               c="Gets the index variable into %rax"))

            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.IRR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c="Gets the index variable into %rax"))


            if t.retReg.regType == 0:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                              c=f"Moves new array into {t.retReg.name}"))
            else:
                self._app(Ins(Operation.MOVE,
                              Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                              Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                              c=f"Moves new array into {t.retReg.name}"))




    def _comparison_op(self, trueJump, t):
        """
            test reg1, reg2
            cond_jump true_label
            movq $0 retReg
            jmp end_label
        true_label:
            movq $1 retReg
        end_label:
        """
        if t.inReg2.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg2), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out into %rcx for cmp"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg2.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out of the stack for cmp"))

        if t.inReg1.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg1), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out into %rax for cmp"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg1.offset)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out of the stack for cmp"))

        self._app(Ins(Operation.CMP,
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT, t.inReg1), Mode(AddressingMode.DIR)),
                      c=f"eval {t.inReg1.name} {t.op} {t.inReg2.name}"))
        self._app(Ins(trueJump,
                      Arg(Target(TargetType.MEM, t.true_label), Mode(AddressingMode.DIR)),
                      c="Jump if the expression was true"))
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, False), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Moves false into %rax"))
        self._app(Ins(Operation.JMP,
                      Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="Jump to end of expression"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.true_label), Mode(AddressingMode.DIR))))
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Moves true into %rax"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR))))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.retReg.name} out into %rax for cmp"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves result into {t.retReg.name}"))
        

    def _arithmetic_op(self, op, t):
        """
                    movq reg1, retReg
                    aritmatic_op reg2, retReg
        """
        if t.inReg2.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg2), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out into %rcx for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg2.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out of the stack for operation"))

        if t.inReg1.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg1), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg1.offset)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out of the stack for operation"))

        self._app(Ins(op,
                      Arg(Target(TargetType.RCX, t.inReg2), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT, t.retReg), Mode(AddressingMode.DIR)),
                      c=f"Operation: {t.inReg1.name} {t.op} {t.retReg.name}"))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves result into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves result into {t.retReg.name}"))



    def _logic_op(self, op, t):
        """
                    movq reg1, retReg
                    logic_op reg2, retReg
        """
        if t.inReg2.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg2), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out into %rcx for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg2.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg2.name} out of the stack for operation"))

        if t.inReg1.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg1), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg1.offset)),
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg1.name} out of the stack for operation"))

        self._app(Ins(op,
                      Arg(Target(TargetType.RCX, t.inReg2), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT, t.retReg), Mode(AddressingMode.DIR)),
                      c=f"Operation: {t.inReg1.name} {t.op} {t.retReg.name}"))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves result into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves result into {t.retReg.name}"))

    def postVisit_expression_binop(self, t):
        if t.op == "==":
            self._comparison_op(Operation.JE, t)
        elif t.op == "!=":
            self._comparison_op(Operation.JNE, t)
        elif t.op == "<":
            self._comparison_op(Operation.JL, t)
        elif t.op == "<=":
            self._comparison_op(Operation.JLE, t)
        elif t.op == ">":
            self._comparison_op(Operation.JG, t)
        elif t.op == ">=":
            self._comparison_op(Operation.JGE, t)
        elif t.op == "+":
            self._arithmetic_op(Operation.ADD, t)
        elif t.op == "-":
            self._arithmetic_op(Operation.SUB, t)
        elif t.op == "*":
            self._arithmetic_op(Operation.MUL, t)
        elif t.op == "/":
            self._arithmetic_op(Operation.DIV, t)
        elif t.op == "%":
            self._arithmetic_op(Operation.MOD, t)
        elif t.op == "&&":
            self._logic_op(Operation.AND, t)
        elif t.op == "||":
            self._logic_op(Operation.OR, t)

    def postVisit_expression_negative(self, t):


        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for operation"))

        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMI, 0), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Move {t.inReg.name} to {t.retReg.name}"))
        self._app(Ins(Operation.SUB,
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Operation: $0 - {t.retReg.name}"))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves result into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves result into {t.retReg.name}"))



    def postVisit_expression_neg(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for operation"))

        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c="Moves true into %rax"))
        self._app(Ins(Operation.CMP,
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Compare: {t.inReg.name} == true"))
        self._app(Ins(Operation.JNE,
                      Arg(Target(TargetType.MEM, t.true_label), Mode(AddressingMode.DIR)),
                      c="Jump if the expression was fasle"))
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, False), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Moves false into {t.retReg.name}"))
        self._app(Ins(Operation.JMP,
                      Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="Jump to end of expression"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.true_label), Mode(AddressingMode.DIR))))
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                      c=f"Moves true into {t.retReg.name}"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR))))

        if t.retReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.REG, t.retReg), Mode(AddressingMode.DIR)),
                          c=f"Moves result into {t.retReg.name}"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RRT), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.retReg.offset)),
                          c=f"Moves result into {t.retReg.name}"))



    def midVisit_statement_ifthen(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for operation"))

        self._app(Ins(Operation.CMP,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      c=f"Compare: {t.inReg.name} == true"))
        self._app(Ins(Operation.JNE,
                      Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="Jump to end if false"))

    def postVisit_statement_ifthen(self, t):
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="end of if"))


    def preMidVisit_statement_ifthenelse(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for operation"))

        self._app(Ins(Operation.CMP,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      c=f"Compare: {t.inReg.name} == true"))
        self._app(Ins(Operation.JNE,
                      Arg(Target(TargetType.MEM, t.else_label), Mode(AddressingMode.DIR)),
                      c="Jump to else if false"))

    def postMidVisit_statement_ifthenelse(self, t):
        self._app(Ins(Operation.JMP,
                      Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="Jump to end"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.else_label), Mode(AddressingMode.DIR)),
                      c="else part"))

    def postVisit_statement_ifthenelse(self, t):
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="end of ifelse"))


    
    def preVisit_statement_while(self, t):
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.begin_label), Mode(AddressingMode.DIR)),
                      c="Start of while"))

    def midVisit_statement_while(self, t):
        if t.inReg.regType == 0:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.REG, t.inReg), Mode(AddressingMode.DIR)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out into %rax for operation"))
        else:
            self._app(Ins(Operation.MOVE,
                          Arg(Target(TargetType.RBX), Mode(AddressingMode.IRL, t.inReg.offset)),
                          Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                          c=f"Moves {t.inReg.name} out of the stack for operation"))

        self._app(Ins(Operation.CMP,
                      Arg(Target(TargetType.IMB, True), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.RCX), Mode(AddressingMode.DIR)),
                      c=f"Compare: {t.inReg.name} == true"))
        self._app(Ins(Operation.JNE,
                      Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="Jump to else if false"))

    def postVisit_statement_while(self, t):
        self._app(Ins(Operation.JMP,
                      Arg(Target(TargetType.MEM, t.begin_label), Mode(AddressingMode.DIR)),
                      c="Jump to start of while"))
        self._app(Ins(Operation.LABEL, Arg(Target(TargetType.MEM, t.end_label), Mode(AddressingMode.DIR)),
                      c="end of while"))

    def postVisit_statement_break(self, t):
        self._app(Ins(Operation.JMP,
                      Arg(Target(TargetType.MEM, t.goto_label), Mode(AddressingMode.DIR)),
                      c="Break of while"))
