#!/usr/bin/env python3

# Copyright (C) 2019
# Kim Skak Larsen
# All rights reserved.
# License: GNU GPLv3

# Description: A compiler is implemented. The implementation is meant for
# teaching purposes. The goal is to illustrate important compiler
# techniques in a simple setting and to enable the students to make
# minor adjustments and extensions. The source language is a simple
# imperative languages with integers being the only type, but including
# expressions, assignment, control structures, and function definitions
# and calls, including recursion and static nested scope. The target
# language is 64 bit x86 assembler using the GNU syntax.

import sys
import getopt

import interfacing_parser
from errors import error_message
from lexer_parser import parser
from symbols import ASTSymbolVisitor
from type_checking import ASTTypeCheckingVisitor
# from pretty_printer import ASTPrettyPrinterVisitor
# from ast_printer import ASTTreePrinterVisitor
from code_generation import ASTCodeGenerationVisitor
from emit import Emit


__version__ = "unfinished beta"


# MAIN

def compiler(showSource, showAST, macOS, input_file, output_file):
    """This function goes through the classic phases of a modern compiler,
    each phase organized in its own module. The phases are:

    parsing:
        handled using the ply package - the parser module includes a lexer,
        and it builds an abstract syntax tree (AST).

    symbol collection:
        collects function, parameter, and variables names, and stores these
        in a symbol table.

    code generation:
        from the AST and symbol table, code is produced in an intermediate
        representation, quite close to the final assembler code.

    emit:
        the slightly abstract intermediate code is transformed to assembler
        code, in a macOS variant if the option is used.
    """

    # Read and verify ASCII input:
    encodingError = False
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

    if showSource or showAST:
            return str(the_program)
    else:

        # Collect names of functions, parameters, and local variables:
        symbols_collector = ASTSymbolVisitor()
        the_program.accept(symbols_collector)

        # Type check use of functions, parameters, and local variables:
        type_checker = ASTTypeCheckingVisitor()
        the_program.accept(type_checker)

        intermediate_code_generator = ASTCodeGenerationVisitor()
        the_program.accept(intermediate_code_generator)
        intermediate_code = intermediate_code_generator.get_code()

        # Emit the target code:
        emitter = Emit(intermediate_code,
                       intermediate_code_generator.getLabelsGenerator(),
                       macOS)
        emitter.emit()
        code = emitter.get_code()

        return code
"""
    else:

        # Collect names of functions, parameters, and local variables:
        symbols_collector = ASTSymbolVisitor()
        the_program.accept(symbols_collector)

        # Type check use of functions, parameters, and local variables:
        type_checker = ASTTypeCheckingVisitor()
        the_program.accept(type_checker)

        # Generate intermediate code:
        intermediate_code_generator = ASTCodeGenerationVisitor()
        the_program.accept(intermediate_code_generator)
        intermediate_code = intermediate_code_generator.get_code()

        # Emit the target code:
        emitter = Emit(intermediate_code,
                       intermediate_code_generator.getLabelsGenerator(),
                       macOS)
        emitter.emit()
        code = emitter.get_code()

        return code
"""

def main(argv):
    usage = f"Usage: {sys.argv[0]} [-hvsm] [-i source_file] [-o target_file]"
    help_text = """
    -h  Print this help text.

    -v  Print the version number.

    -s  Print back the parsed source code instead of target code.

    -a  Print the AST in dot format instead of target code.

    -m  Generate assembly code for macOS.

    -i source_file  Set source file; default is stdin.

    -o target_file  Set target file; default is stdout.
    """
    input_file = ""
    output_file = ""
    show_source = False
    show_ast = False
    macOS = False
    try:
        opts, args = getopt.getopt(argv, "hsamvi:o:")
    except getopt.GetoptError:
        print(usage)
        sys.exit(1)
    for opt, arg in opts:
        if opt == "-h":
            print(usage)
            print(help_text)
            sys.exit(0)
        elif opt == "-v":
            print(__version__)
            sys.exit(0)
        elif opt == "-s":
            show_source = True
        elif opt == "-a":
            show_ast = True
        elif opt == "-m":
            macOS = True
        elif opt == "-i":
            input_file = arg
        elif opt == "-o":
            output_file = arg
    result = compiler(show_source, show_ast, macOS, input_file, output_file)
    if output_file:
        f = open(output_file, "w")
        f.write(result)
        f.close()
    else:
        print(result)


if __name__ == "__main__":
    main(sys.argv[1:])
