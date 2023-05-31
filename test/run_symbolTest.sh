#!/bin/bash

# This script runs all the tests in the parserTest directory and saves the output to .out files
COMPILER_COMMAND="python ../src/compiler.py -s -i"
PARSER_TEST_DIR="./symbolTest"

# Get all the test files
TEST_FILES=$(find $PARSER_TEST_DIR -name "*.leif")

# Set the log file name
LOG_FILE="testLogSymbol.txt"
echo "" > $LOG_FILE

# Initialize counters for total tests and successful tests
total_tests=0
successful_tests=0

# Iterate through the test files, run them with the compiler, and save the results to .out files
for file in $TEST_FILES; do
  echo "Running test: $file" | tee -a $LOG_FILE
  # Replace the file extension .leif with .out
  out_file="${file%.leif}.out"
  # Run the compiler command, redirecting stdout and stderr to the .out file
  if $COMPILER_COMMAND $file &> $out_file; then
    successful_tests=$((successful_tests + 1))
  fi
  total_tests=$((total_tests + 1))
done
total_failed=$((total_tests - successful_tests))
echo "All tests completed." | tee -a $LOG_FILE
echo "failed test: $total_failed  " | tee -a $LOG_FILE
echo "Total tests run: $total_tests" | tee -a $LOG_FILE
