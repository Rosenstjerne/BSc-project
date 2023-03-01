
# Since lexing and parsing is handled via the ply module, the current
# module functions as the interface between the module and the rest
# of the compiler. If there are no parsing errors, the_program will
# contain the abstract syntax tree of the input program.


the_program = None