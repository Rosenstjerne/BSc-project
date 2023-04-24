
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

                movq $6, %r8            # Moves integer into reg0
                movq $5, %r9            # Moves integer into reg1
                movq $4, %r10           # Moves integer into reg2
                movq %r10, %r11         # Move reg2 to reg3
                imulq %r9, %r11         # Operation: reg1 * reg3
                movq %r11, %r9          # Move reg3 to reg4
                addq %r8, %r9           # Operation: reg0 + reg4
                movq $9, %r8            # Moves integer into reg5
                movq $2, %r10           # Moves integer into reg6
                movq %r10, %r11         # Move reg6 to reg7
                subq %r8, %r11          # Operation: reg5 - reg7
                movq %r11, %r8          # Move reg7 to reg8
                addq %r9, %r8           # Operation: reg4 + reg8
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into reg9
                movq $1, %r9            # Moves boolean into reg10
                movq %r8, %r10          # Move reg10 to reg11
                orq %r9, %r10           # Operation: reg9 || reg11
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r10, %rsi         # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $2, %r8            # Moves integer into reg12
                movq $2, %r9            # Moves integer into reg13
                movq %r9, %r10          # Move reg13 to reg14
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
                movq $5, %r8            # Moves integer into reg15
                movq $3, %r9            # Moves integer into reg16
                movq %r9, %r10          # Move reg16 to reg17
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
                movq $1, %r8            # Moves integer into reg18
                movq $2, %r9            # Moves integer into reg19
                cmpq %r8, %r9           # eval reg18 < reg19
                jl lbl0_cmp_true        # Jump if the expression was true
                movq $0, %r8            # Moves false into reg20
                jmp lbl1_cmp_end        # Jump to end of expression
lbl0_cmp_true:
                movq $1, %r8            # Moves true into reg20
lbl1_cmp_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg21
                movq $5, %r9            # Moves integer into reg22
                cmpq %r8, %r9           # eval reg21 == reg22
                je lbl2_cmp_true        # Jump if the expression was true
                movq $0, %r8            # Moves false into reg23
                jmp lbl3_cmp_end        # Jump to end of expression
lbl2_cmp_true:
                movq $1, %r8            # Moves true into reg23
lbl3_cmp_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $7, %r8            # Moves integer into reg24
                movq $9, %r9            # Moves integer into reg25
                cmpq %r8, %r9           # eval reg24 >= reg25
                jge lbl4_cmp_true       # Jump if the expression was true
                movq $0, %r8            # Moves false into reg26
                jmp lbl5_cmp_end        # Jump to end of expression
lbl4_cmp_true:
                movq $1, %r8            # Moves true into reg26
lbl5_cmp_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg27
                movq %r8, %r9           # Move reg27 to reg28
                subq $0, %r9            # Operation: $0 - reg28
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r9, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $1, %r8            # Moves boolean into reg29
                cmpq %r8, $1            # Compare: reg29 == true
                je lbl6_exp_neg_true    # Jump if the expression was true
                movq $0, %r8            # Moves false into reg30
                jmp lbl7_exp_neg_end    # Jump to end of expression
lbl6_exp_neg_true:
                movq $1, %r8            # Moves true into reg30
lbl7_exp_neg_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $4, %r8            # Moves integer into reg31
                movq $5, %r9            # Moves integer into reg32
                cmpq %r8, %r9           # eval reg31 < reg32
                jl lbl8_cmp_true        # Jump if the expression was true
                movq $0, %r8            # Moves false into reg33
                jmp lbl9_cmp_end        # Jump to end of expression
lbl8_cmp_true:
                movq $1, %r8            # Moves true into reg33
lbl9_cmp_end:
                cmpq %r8, $1            # Compare: reg33 == true
                jne lbl10_if_end        # Jump to end if false
                movq $8, %r8            # Moves integer into reg34
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
lbl10_if_end:
                movq $1, %r8            # Moves boolean into reg35
                cmpq %r8, $1            # Compare: reg35 == true
                jne lbl11_if_else_else  # Jump to else if false
                movq $1, %r8            # Moves boolean into reg36
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                jmp lbl12_if_else_end   # Jump to end
lbl11_if_else_else:
                movq $1, %r8            # Moves boolean into reg37
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
lbl12_if_else_end:
lbl15_while_begin:
                movq $1, %r8            # Moves boolean into reg38
                cmpq %r8, $1            # Compare: reg38 == true
                je lbl13_exp_neg_true   # Jump if the expression was true
                movq $0, %r8            # Moves false into reg39
                jmp lbl14_exp_neg_end   # Jump to end of expression
lbl13_exp_neg_true:
                movq $1, %r8            # Moves true into reg39
lbl14_exp_neg_end:
                cmpq %r8, $1            # Compare: reg39 == true
                jne lbl16_while_end     # Jump to else if false
                movq $8, %r8            # Moves integer into reg40
                movq $5, %r9            # Moves integer into reg41
                cmpq %r8, %r9           # eval reg40 != reg41
                jne lbl17_cmp_true      # Jump if the expression was true
                movq $0, %r8            # Moves false into reg42
                jmp lbl18_cmp_end       # Jump to end of expression
lbl17_cmp_true:
                movq $1, %r8            # Moves true into reg42
lbl18_cmp_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                jmp lbl15_while_begin   # Jump to start of while
lbl16_while_end:
lbl19_while_begin:
                movq $1, %r8            # Moves boolean into reg43
                cmpq %r8, $1            # Compare: reg43 == true
                jne lbl20_while_end     # Jump to else if false
                movq $1, %r8            # Moves boolean into reg44
                cmpq %r8, $1            # Compare: reg44 == true
                jne lbl25_if_else_else  # Jump to else if false
                movq $1, %r8            # Moves boolean into reg45
                cmpq %r8, $1            # Compare: reg45 == true
                je lbl21_exp_neg_true   # Jump if the expression was true
                movq $0, %r8            # Moves false into reg46
                jmp lbl22_exp_neg_end   # Jump to end of expression
lbl21_exp_neg_true:
                movq $1, %r8            # Moves true into reg46
lbl22_exp_neg_end:
                cmpq %r8, $1            # Compare: reg46 == true
                je lbl23_exp_neg_true   # Jump if the expression was true
                movq $0, %r8            # Moves false into reg47
                jmp lbl24_exp_neg_end   # Jump to end of expression
lbl23_exp_neg_true:
                movq $1, %r8            # Moves true into reg47
lbl24_exp_neg_end:
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                movq $5, %r8            # Moves integer into reg48
                movq %r8, %r9           # Move reg48 to reg49
                subq $0, %r9            # Operation: $0 - reg49
                movq %r9, %r8           # Move reg49 to reg50
                subq $0, %r8            # Operation: $0 - reg50
                                        # PRINTING
                leaq form(%rip), %rdi   # pass 1. argument in %rdi
                movq %r8, %rsi          # Moves printable object to rsi
                xorq %rax, %rax         # No floating point arguments

                callq printf@plt        # calls the printf method
                                        # END OF PRINTING
                jmp lbl26_if_else_end   # Jump to end
lbl25_if_else_else:
                jmp lbl20_while_end     # Break of while
lbl26_if_else_end:
                jmp lbl19_while_begin   # Jump to start of while
lbl20_while_end:
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


