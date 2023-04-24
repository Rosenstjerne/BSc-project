
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

                movq $6, %r8            # Moves integer into %r8
                movq $5, %r8            # Moves integer into %r8
                movq $4, %r9            # Moves integer into %r9
                movq %r9, %r10          # 
                imulq %r8, %r10         # Operation: *
                movq %r10, %r9          # 
                addq %r8, %r9           # Operation: +
                movq $9, %r8            # Moves integer into %r8
                movq $2, %r9            # Moves integer into %r9
                movq %r9, %r10          # 
                subq %r8, %r10          # Operation: -
                movq %r10, %r8          # 
                addq %r9, %r8           # Operation: +
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into %r8
                movq $1, %r9            # Moves boolean into %r9
                movq %r8, %r10          # 
                orq %r9, %r10           # Operation: ||
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $2, %r8            # Moves integer into %r8
                movq $2, %r9            # Moves integer into %r9
                movq %r9, %r10          # 
                movq %r10, %rax         # prepare for division
                cqo                     # sign extend
                idivq %r8               # divide
                movq %rax, %r10         # move to destination
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $5, %r8            # Moves integer into %r8
                movq $3, %r9            # Moves integer into %r9
                movq %r9, %r10          # 
                movq %r10, %rax         # prepare for modulo
                cqo                     # sign extend
                idivq %r8               # modulo
                movq %rdx, %r10         # move to destination
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves integer into %r8
                movq $2, %r9            # Moves integer into %r9
                cmpq %r8, %r9           # 
                jl label_0              # Jump if the expression was true
                movq $0, %r10           # Moves false into %r10
                jmp label_1             # Jump to end of expression
label_0:
                movq $1, %r10           # Moves true into %r10
label_1:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into %r8
                movq $5, %r9            # Moves integer into %r9
                cmpq %r8, %r9           # 
                je label_2              # Jump if the expression was true
                movq $0, %r10           # Moves false into %r10
                jmp label_3             # Jump to end of expression
label_2:
                movq $1, %r10           # Moves true into %r10
label_3:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $7, %r8            # Moves integer into %r8
                movq $9, %r9            # Moves integer into %r9
                cmpq %r8, %r9           # 
                jge label_4             # Jump if the expression was true
                movq $0, %r10           # Moves false into %r10
                jmp label_5             # Jump to end of expression
label_4:
                movq $1, %r10           # Moves true into %r10
label_5:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into %r8
                movq %r8, %r9           # 
                subq $0, %r9            # 
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r9, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into %r8
                cmpq %r8, $1            # 
                je label_6              # Jump if the expression was true
                movq $0, %r9            # Moves false into %r9
                jmp label_7             # Jump to end of expression
label_6:
                movq $1, %r9            # Moves true into %r9
label_7:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r9, %rsi          # Moves printable object to rsi
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


