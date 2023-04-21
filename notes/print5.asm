form:
                .string "%d\n"          # form string for C printf


movq $5, reg1 #saves 5 to a general resister     

# PRINTING
leaq form(%rip), %rdi   
movq reg1, %rsi     
xorq %rax, %rax         

callq printf@plt
