
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
    REG = auto()  # general-purpose registers


class AddressingMode(Enum):
    """Defines an enumeration type for addressing modes. """
    DIR = auto()  # direct
    IND = auto()  # indirect
    IRL = auto()  # indirect relative


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

    
    def get_code(self):
        return self._code


    def _app(self, instruction):
        self._code.append(instruction)

    
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


    def postVisit_statement_return(self, t):
        # Getting the function label from the nearest enclosing function:
        label = self._function_stack[-1].end_label
        self._app(Ins(Operation.RET, 
                      Arg(Target(TargetType.REG, t.inReg.getReg()), Mode(AddressingMode.DIR)),
                      c=label))


    def postVisit_statement_print(self, t):
        self._app(Ins(Operation.META, 
                      Meta.CALL_PRINTF,
                      Arg(Target(TargetType.REG, t.inReg.getReg()), Mode(AddressingMode.DIR))
                      ))

    
    def postVisit_expression_integer(self, t):
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMI, t.integer), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.REG, t.retReg.getReg()), Mode(AddressingMode.DIR)),
                      c=f"Moves integer into {t.retReg.getReg()}"))
        
    def postVisit_expression_boolean(self, t):
        self._app(Ins(Operation.MOVE,
                      Arg(Target(TargetType.IMB, t.boolean), Mode(AddressingMode.DIR)),
                      Arg(Target(TargetType.REG, t.retReg.getReg()), Mode(AddressingMode.DIR)),
                      c=f"Moves boolean into {t.retReg.getReg()}"))
