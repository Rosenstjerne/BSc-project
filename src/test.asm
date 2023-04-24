
.data

form:
                .string "%d\n"          # form string for C printf

.text

.globl main

fun_1_main:

                                        # CALLEE PROLOGUE
                pushq %rbp              # save caller's base pointer
                movq %rsp, %rbp         # make stack pointer new base pointer

                addq $0, %rsp           # allocate space for local variables


                pushq %rbx              # %rbx is callee save
                pushq %r8               # %r8 is callee save
                pushq %r9               # %r9 is callee save
                pushq %r10              # %r10 is callee save
                pushq %r11              # %r11 is callee save
                pushq %r12              # %r12 is callee save
                pushq %r13              # %r13 is callee save
                pushq %r14              # %r14 is callee save
                pushq %r15              # %r15 is callee save

                movq $5, %r8            # Moves integer into %r8
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
end_main:

                popq %r15               # restore callee save register %r15
                popq %r14               # restore callee save register %r14
                popq %r13               # restore callee save register %r13
                popq %r12               # restore callee save register %r12
                popq %r11               # restore callee save register %r11
                popq %r10               # restore callee save register %r10
                popq %r9                # restore callee save register %r9
                popq %r8                # restore callee save register %r8
                popq %rbx               # restore callee save register %rbx


                                        # CALLEE EPILOGUE
                movq %rbp, %rsp         # restore stack pointer
                popq %rbp               # restore base pointer
                ret                     # return from call


