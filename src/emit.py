from code_generation import Operation, TargetType, AddressingMode, Meta

_intermediate_to_x86 = {
    Operation.MOVE: "movq",
    Operation.CALL: "callq",
    Operation.PUSH: "pushq",
    Operation.POP: "popq",
    Operation.CMP: "cmpq",
    Operation.JMP: "jmp",
    Operation.JE: "je",
    Operation.JNE: "jne",
    Operation.JL: "jl",
    Operation.JLE: "jle",
    Operation.JG: "jg",
    Operation.JGE: "jge",
    Operation.ADD: "addq",
    Operation.SUB: "subq",
    Operation.MUL: "imulq",
    Operation.AND: "andq",
    Operation.OR: "orq",
    }


# Emitting


class Emit:
    """The class that emits 64 bit x86 assembler code. Attempts are made
       to make the code human readable.
    """
    def __init__(self, intermediate_representation, extra_intermediate_regs):
        self.intermediate_representation = intermediate_representation
        # The unique labels generator:
        self.instruction_indent = 16
        self.instruction_width = 24
        self.max_width = 79
        self.code = []
        self.lbl_counter = 0
        self.extra_intermediate_regs = extra_intermediate_regs

    def getLbl(self):
        lbl = f"LBL_{self.lbl_counter}"
        self.lbl_counter += 1
        return lbl

    def emit(self):
        self.program_prologue()
        for instruction in self.intermediate_representation:
            self._dispatch(instruction)
        self.program_epilogue()

    def get_code(self):
        self.code.append("\n")
        return "\n".join(self.code)

    def _format_comment(self, comment):
        """Formats comments that would make the total line length too large
           by using multiple lines.
        """
        width = self.max_width-self.instruction_indent-self.instruction_width-2
        page = []
        line = ""
        for word in comment.split():
            if not line:
                line += word
            else:
                if len(line) + 1 + len(word) <= width:
                    line += " " + word
                else:
                    page.append(line)
                    line = word
        if line:
            page.append(line)
        delimiter = "\n" + (self.max_width - width - 2) * " " + "# "
        return delimiter.join(page)

    # The following three methods append to self.code:

    def _lbl(self, lbl):
        self.code.append(lbl + ":")

    def _ins(self, instr_str, comment):
        line = self.instruction_indent * " " \
               + instr_str.ljust(self.instruction_width) \
               + "# " + self._format_comment(comment)
        self.code.append(line)

    def _raw(self, s):
        self.code.append(s)

    # Emitting intermediate representation instructions:

    def _dispatch(self, instr):
        if instr.opcode in _intermediate_to_x86:
            self._simple_instruction(instr)
        elif instr.opcode is Operation.DIV:
            self._div(instr)
        elif instr.opcode is Operation.MOD:
            self._mod(instr)
        elif instr.opcode is Operation.LABEL:
            self._label(instr)
        elif instr.opcode is Operation.META:
            method = instr.args[0]
            if method is Meta.MAIN_CALLEE_SAVE:
                self.main_callee_save()
            elif method is Meta.MAIN_CALLEE_RESTORE:
                self.main_callee_restore()
            if method is Meta.CALLER_SAVE:
                self.caller_save()
            elif method is Meta.CALLER_RESTORE:
                self.caller_restore()
            elif method is Meta.CALLEE_PROLOGUE:
                self.callee_prologue()
            elif method is Meta.CALLEE_EPILOGUE:
                self.callee_epilogue()
            elif method is Meta.CALL_PRINTF:
                self.call_printf(instr)
            elif method is Meta.ALLOCATE_STACK_SPACE:
                self.allocate_stack_space(instr.args[1])
            elif method is Meta.ALLOCATE_HEAP_SPACE:
                self.allocate_heap_space()

    def _do_arg(self, arg):
        """Formats one instruction argument."""
        target = arg.target
        text = ""
        if target.spec is TargetType.IMI:  # Immidiate Integer or Lable
            text = f"${target.val}"
        elif target.spec is TargetType.IMB:
            text = f"${1 if target.val == True else 0}"  # Immidiate boolean
        elif target.spec is TargetType.MEM:
            text = f"{target.val}"
        elif target.spec is TargetType.RBP:
            text = "%rbp"
        elif target.spec is TargetType.RRT:
            text = "%rax"
        elif target.spec is TargetType.RSL:
            text = "%rdx"
        elif target.spec is TargetType.RBX:
            text = "%rbx"
        elif target.spec is TargetType.RCX:
            text = "%rcx"
        elif target.spec is TargetType.REG:
            text = target.val.getReg()

        addressing = arg.addressing
        if addressing.mode is AddressingMode.DIR:
            pass
        elif addressing.mode is AddressingMode.IRL:
            text = f"{-8*addressing.offset}({text})"
        elif addressing.mode is AddressingMode.IRR:
            text = f"({text}, %rcx, 8)"
        return text

    def _simple_instruction(self, instr):
        """Most instructions simply have their opcode translated to the
           64 bit x86 syntax and their one or two parameters formated by
           _do_arg. This method implements this generically.
        """
        line = _intermediate_to_x86[instr.opcode]
        if len(instr.args) > 0:
            line += " " + self._do_arg(instr.args[0])
        for i in range(1, len(instr.args)):
            line += ", " + self._do_arg(instr.args[i])
        self._ins(line, instr.comment)

    # The few instruction that do not follow the simple pattern:

    def _div(self, instr):
        self._ins(f"movq {self._do_arg(instr.args[1])}, %rax",
                  "prepare for division")
        self._ins("cqo", "sign extend")
        self._ins(f"idivq {self._do_arg(instr.args[0])}", "divide")
        self._ins(f"movq %rax, {self._do_arg(instr.args[1])}",
                  "move to destination")

    def _mod(self, instr):
        self._ins(f"movq {self._do_arg(instr.args[1])}, %rax",
                  "prepare for modulo")
        self._ins("cqo", "sign extend")
        self._ins(f"idivq {self._do_arg(instr.args[0])}", "modulo")
        self._ins(f"movq %rdx, {self._do_arg(instr.args[1])}",
                  "move to destination")

    def _label(self, instr):
        self._lbl(self._do_arg(instr.args[0]))


    # Block code for prologues, epilogues, printing, etc.:

    def program_prologue(self):
        self._raw("")
        self._raw(".data")
        self._lbl("mmapEr")
        self._ins('.string "mmap failed\\n"', "error message string for mmap")
        self._raw("")
        self._lbl("form")
        self._ins('.string "%d\\n"', "form string for C printf")
        self._raw("")
        self._lbl("formTrue")
        self._ins('.string "true\\n"', "form string for C printf")
        self._raw("")
        self._lbl("formFalse")
        self._ins('.string "false\\n"', "form string for C printf")
        self._raw("")
        self._raw(".text")
        self._raw("")
        self._raw(f".globl main")
        self._raw("")

    def program_epilogue(self):
        self._raw("")
        self._raw("mmap_error:")
        self._ins("leaq mmapEr(%rip), %rdi", " pass 1. arg in %rdi")
        self._ins("xor %rax, %rax", "no floating point arguments")
        self._ins("callq printf", "calls printf method")
        self._raw("")
        self._ins("movq $60, %rax", "prepare for exit syscall")
        self._ins("xor %rdi, %rdi", "exit status 0")
        self._ins("syscall", "exit")


    def main_callee_save(self):
        self._raw("")
        self._ins("movq %rsp, %rbx", "Saves stack pointer in %rbx")
        self._ins(f"addq ${-8*self.extra_intermediate_regs}, %rsp",
                  "allocate space for extra intermediate stack memory")
        self._raw("")
        self._ins("pushq %r8",  "%r8  is callee save")
        self._ins("pushq %r9",  "%r9  is callee save")
        self._ins("pushq %r10", "%r10 is callee save")
        self._ins("pushq %r11", "%r11 is callee save")
        self._ins("pushq %r12", "%r12 is callee save")
        self._ins("pushq %r13", "%r13 is callee save")
        self._ins("pushq %r14", "%r14 is callee save")
        self._ins("pushq %r15", "%r15 is callee save")
        self._raw("")

    def main_callee_restore(self):
        self._raw("")
        self._ins("popq %r15", "restore callee save register %r15")
        self._ins("popq %r14", "restore callee save register %r14")
        self._ins("popq %r13", "restore callee save register %r13")
        self._ins("popq %r12", "restore callee save register %r12")
        self._ins("popq %r11", "restore callee save register %r11")
        self._ins("popq %r10", "restore callee save register %r10")
        self._ins("popq %r9",  "restore callee save register %r9 ")
        self._ins("popq %r8",  "restore callee save register %r8 ")
        self._raw("")
        self._ins(f"addq ${8*self.extra_intermediate_regs}, %rsp",
                  "deallocate stack space for extra intermediate stack memory")
        self._raw("")

    def caller_save(self):
        self._raw("")
        self._ins("pushq %r8",  "%r8  is callee save")
        self._ins("pushq %r9",  "%r9  is callee save")
        self._ins("pushq %r10", "%r10 is callee save")
        self._ins("pushq %r11", "%r11 is callee save")
        self._ins("pushq %r12", "%r12 is callee save")
        self._ins("pushq %r13", "%r13 is callee save")
        self._ins("pushq %r14", "%r14 is callee save")
        self._ins("pushq %r15", "%r15 is callee save")
        for i in range(self.extra_intermediate_regs-1,-1,-1):
            self._ins(f"pushq {-8*i}(%rbx)", "stack reg save")
        self._raw("")

    def caller_restore(self):
        self._raw("")
        for i in range(self.extra_intermediate_regs):
            self._ins(f"popq {-8*i}(%rbx)", "stack reg save")
        self._ins("popq %r15", "restore callee save register %r15")
        self._ins("popq %r14", "restore callee save register %r14")
        self._ins("popq %r13", "restore callee save register %r13")
        self._ins("popq %r12", "restore callee save register %r12")
        self._ins("popq %r11", "restore callee save register %r11")
        self._ins("popq %r10", "restore callee save register %r10")
        self._ins("popq %r9",  "restore callee save register %r9 ")
        self._ins("popq %r8",  "restore callee save register %r8 ")
        self._raw("")

    def callee_prologue(self):
        self._raw("")
        self._ins("", "CALLEE PROLOGUE")
        self._ins("pushq %rbp", "save caller's base pointer")
        self._ins("movq %rsp, %rbp", "make stack pointer new base pointer")
        self._raw("")

    def callee_epilogue(self):
        self._raw("")
        self._ins("", "CALLEE EPILOGUE")
        self._ins("movq %rbp, %rsp", "restore stack pointer")
        self._ins("popq %rbp", "restore base pointer")
        self._ins("ret", "return from call")
        self._raw("")

    def call_printf(self, instr):
        self._ins("", "PRINTING")
        if instr.args[1] == "bool":
            self._ins(f"movq $1, %rax", "Moves true into %rax")
            self._ins(f"cmpq %rcx, %rax","")
            true_lbl = self.getLbl()
            end_lbl = self.getLbl()
            self._ins(f"je {true_lbl}","")
            self._ins("leaq formFalse(%rip), %rdi", "pass 1. argument in %rdi")
            self._ins(f"jmp {end_lbl}","")
            self._lbl(true_lbl)
            self._ins("leaq formTrue(%rip), %rdi", "pass 1. argument in %rdi")
            self._lbl(end_lbl)
        else:
            self._ins("leaq form(%rip), %rdi", "pass 1. argument in %rdi")
        # By-passing caller save values on the stack:
        self._ins(f"movq %rcx, %rsi","Moves printable object to rsi")
        self._ins("xorq %rax, %rax","No floating point arguments") 
        self._raw("")
        self._ins("callq printf@plt","calls the printf method")
        self._ins("","END OF PRINTING")



    def allocate_stack_space(self, words):
        self._ins(f"addq ${-8*words}, %rsp",
                  "allocate space for local variables")
        self._raw("")

    def allocate_heap_space(self):
            self._ins("pushq %rdx", "%rdx is caller save")
            self._ins("pushq %rsi", "%rsi is caller save")
            self._ins("pushq %rdi", "%rdi is caller save")
            self._ins("pushq %r8",  "%r8  is caller save")
            self._ins("pushq %r9",  "%r9  is caller save")
            self._ins("pushq %r10",  "%r10  is caller save")
            self._ins("pushq %r15",  "%r15  is caller save")
            self._raw("")

            self._ins("movq %rcx, %rsi", "moves size form %rxc into %rsi")
            self._ins("movq %rcx, %r15", "moves size form %rxc into %r15")
            self._ins("shlq $3, %rsi", "")
            self._ins("xorq %rdi, %rdi", "")
            self._ins("movq $9, %rax", "prepare mmap syscall")
            self._ins("movq $0x3, %rdx", "")
            self._ins("xorq %r8, %r8", "")
            self._ins("xorq %r9, %r9", "")
            self._ins("movq $0x22, %r10", "")
            self._ins("syscall","allocates the memory")
            self._raw("")
            self._ins("cmpq $-22, %rax", "checks if mmap was successful")
            self._ins("je mmap_error", "jumps to mmap error if not")
            self._raw("")
            start_lbl = self.getLbl()
            end_lbl = self.getLbl()

            self._ins("movq $0, %r10","initializes the index")
            self._lbl(start_lbl)
            self._ins("cmpq %r15, %r10","if the index is at the end")
            self._ins(f"je {end_lbl}","Jumps to end when all is initializes")
            self._ins("movq $0, (%rax, %r10, 8)","initializes the index")
            self._ins("incq %r10","increment the index")
            self._ins(f"jmp {start_lbl}","")
            self._lbl(end_lbl)
            self._raw("")

            self._ins("popq %r15",  "restore caller save register %r15 ")
            self._ins("popq %r10",  "restore caller save register %r10 ")
            self._ins("popq %r9",  "restore caller save register %r9 ")
            self._ins("popq %r8",  "restore caller save register %r8 ")
            self._ins("popq %rdi", "restore caller save register %rdi")
            self._ins("popq %rsi", "restore caller save register %rsi")
            self._ins("popq %rdx", "restore caller save register %rdx")

