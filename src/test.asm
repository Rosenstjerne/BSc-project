
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

                movq $6, %r8            # Moves integer into reg_0
                movq $5, %r9            # Moves integer into reg_1
                movq $4, %r10           # Moves integer into reg_2
                movq %r10, %r11         # Move reg_2 to reg_3
                imulq %r9, %r11         # Operation: reg_1 * reg_3
                movq %r11, %r9          # Move reg_3 to reg_4
                addq %r8, %r9           # Operation: reg_0 + reg_4
                movq $9, %r8            # Moves integer into reg_5
                movq $2, %r10           # Moves integer into reg_6
                movq %r10, %r11         # Move reg_6 to reg_7
                subq %r8, %r11          # Operation: reg_5 - reg_7
                movq %r11, %r8          # Move reg_7 to reg_8
                addq %r9, %r8           # Operation: reg_4 + reg_8
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into reg_9
                movq $1, %r9            # Moves boolean into reg_10
                movq %r8, %r10          # Move reg_10 to reg_11
                orq %r9, %r10           # Operation: reg_9 || reg_11
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $2, %r8            # Moves integer into reg_12
                movq $2, %r9            # Moves integer into reg_13
                movq %r9, %r10          # Move reg_13 to reg_14
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
                movq $5, %r8            # Moves integer into reg_15
                movq $3, %r9            # Moves integer into reg_16
                movq %r9, %r10          # Move reg_16 to reg_17
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
                movq $1, %r8            # Moves integer into reg_18
                movq $2, %r9            # Moves integer into reg_19
                cmpq %r8, %r9           # eval reg_18 < reg_19
                jl label_0              # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_20
                jmp label_1             # Jump to end of expression
label_0:
                movq $1, %r8            # Moves true into reg_20
label_1:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg_21
                movq $5, %r9            # Moves integer into reg_22
                cmpq %r8, %r9           # eval reg_21 == reg_22
                je label_2              # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_23
                jmp label_3             # Jump to end of expression
label_2:
                movq $1, %r8            # Moves true into reg_23
label_3:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $7, %r8            # Moves integer into reg_24
                movq $9, %r9            # Moves integer into reg_25
                cmpq %r8, %r9           # eval reg_24 >= reg_25
                jge label_4             # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_26
                jmp label_5             # Jump to end of expression
label_4:
                movq $1, %r8            # Moves true into reg_26
label_5:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg_27
                movq %r8, %r9           # Move reg_27 to reg_28
                subq $0, %r9            # Operation: $0 - reg_28
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r9, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into reg_29
                cmpq %r8, $1            # Compare: reg_29 == true
                je label_6              # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_30
                jmp label_7             # Jump to end of expression
label_6:
                movq $1, %r8            # Moves true into reg_30
label_7:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg_31
                movq $5, %r9            # Moves integer into reg_32
                cmpq %r8, %r9           # eval reg_31 < reg_32
                jl label_8              # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_33
                jmp label_9             # Jump to end of expression
label_8:
                movq $1, %r8            # Moves true into reg_33
label_9:
                cmpq %r8, $1            # Compare: reg_33 == true
                jne label_10            # Jump to end if false
                movq $8, %r8            # Moves integer into reg_34
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
label_10:
                movq $1, %r8            # Moves boolean into reg_35
                cmpq %r8, $1            # Compare: reg_35 == true
                jne label_11            # Jump to else if false
                movq $1, %r8            # Moves boolean into reg_36
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                jmp label_12            # Jump to end
label_11:
                movq $1, %r8            # Moves boolean into reg_37
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
label_12:
label_17:
                movq $1, %r8            # Moves boolean into reg_38
                cmpq %r8, $1            # Compare: reg_38 == true
                je label_13             # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_39
                jmp label_14            # Jump to end of expression
label_13:
                movq $1, %r8            # Moves true into reg_39
label_14:
                cmpq %r8, $1            # Compare: reg_39 == true
                jne label_18            # Jump to else if false
                movq $8, %r8            # Moves integer into reg_40
                movq $5, %r9            # Moves integer into reg_41
                cmpq %r8, %r9           # eval reg_40 != reg_41
                jne label_15            # Jump if the expression was true
                movq $0, %r8            # Moves false into reg_42
                jmp label_16            # Jump to end of expression
label_15:
                movq $1, %r8            # Moves true into reg_42
label_16:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                jmp label_17            # Jump to start of while
label_18:
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


