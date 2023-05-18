#!/usr/bin/env python3

import sys
import getopt

import interfacing_parser
from errors import error_message
from lexer_parser import parser
from symbols import ASTSymbolVisitor
from type_checking import ASTTypeCheckingVisitor
from code_generation import ASTCodeGenerationVisitor
from emit import Emit
from symbol_table_flattener import ASTTabFlattener
from reg_distributor import ASTRegDistributor
from function_decoupeler import ASTFunDecouple

__version__ = "unfinished alpha"

# MAIN

def compiler(showSource, input_file):

    # Read and verify ASCII input:
    encodingError = False
    text = ""
    try:
        if input_file:
            with open(input_file) as f:
                text = f.read()
        else:
            text = sys.stdin.read()
        try:
            text.encode("ascii")
        except UnicodeEncodeError:  # Check for non-ascii
            encodingError = True
    except UnicodeDecodeError:  # Check for unicode
        encodingError = True
    if encodingError:
        error_message("Set-Up", "The input is not in ASCII.", 1)

    # Parse input text:
    parser.parse(text)

    # the_program is the resulting AST:
    the_program = interfacing_parser.the_program
    if the_program is None:
        return ""

    if showSource:
            return str(the_program)
    else:

        # Collect names of functions, parameters, and local variables:
        symbols_collector = ASTSymbolVisitor()
        the_program.accept(symbols_collector)

        # Type check use of functions, parameters, and local variables:
        type_checker = ASTTypeCheckingVisitor()
        the_program.accept(type_checker)

        # Flattens the symbol table
        symTab_flattener = ASTTabFlattener() 
        the_program.accept(symTab_flattener)

        # Distributes the register needed for the intermediate operations
        register_distributor = ASTRegDistributor(symTab_flattener.var_table)
        the_program.accept(register_distributor)
        register_distributor.colorRegisters()

        fun_decoupeler = ASTFunDecouple()
        the_program.accept(fun_decoupeler)
        function_list = fun_decoupeler.getFunctions()

        intermediate_code_generator = ASTCodeGenerationVisitor(symTab_flattener.var_table)
        for f in function_list:
            f.accept(intermediate_code_generator)

        intermediate_code = intermediate_code_generator.get_code()

        # Emit the target code:
        emitter = Emit(intermediate_code, register_distributor.getExterRegisterCount())
        emitter.emit()
        code = emitter.get_code()

        return code

def main(argv):

    usage = f"Usage: {sys.argv[0]} [-hvs] [-i source_file] [-o target_file]"
    help_text = """
    -h  Print this help text.

    -v  Print the version number.

    -s  Print back the parsed source code instead of target code.

    -i source_file  Set source file; default is stdin.

    -o target_file  Set target file; default is stdout.
    """
    input_file = ""
    output_file = ""
    show_source = False
    try:
        opts, args = getopt.getopt(argv, "hsvi:o:")
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            print(help_text)
            # sys.exit(0)
        elif opt == "-v":
            print(__version__)
            # sys.exit(0)
        elif opt == "-s":
            show_source = True
        elif opt == "-i":
            input_file = arg
        elif opt == "-o":
            output_file = arg
    if input_file:
        result = compiler(show_source, input_file)
    else:
        result = ""
    if output_file:
        f = open(output_file, "w")
        f.write(result)
        f.close()
    else:
        print(result)


if __name__ == "__main__":
    main(sys.argv[1:])
