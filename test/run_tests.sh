#!/bin/bash

# This script runs all the tests in the parserTest directory and saves the output to .out files
COMPILER_COMMAND="python ../src/compiler.py -c 1 -i"
PARSER_TEST_DIR="./parserTest"

# Get all the test files
TEST_FILES=$(find $PARSER_TEST_DIR -name "*.leif")

# Set the log file name
LOG_FILE="testLog.txt"
echo "" > $LOG_FILE

# Initialize counters for total tests and successful tests
total_tests=0
successful_tests=0

# Iterate through the test files, run them with the compiler, and save the results to .out files
for file in $TEST_FILES; do
  echo "Running test: $file" | tee -a $LOG_FILE
  # Replace the file extension .leif with .out
  out_file="${file%.leif}.out"
  # Run the compiler command, redirecting stdout to the .out file and stderr to the log file
  if $COMPILER_COMMAND $file > $out_file 2>> $LOG_FILE; then
    successful_tests=$((successful_tests + 1))
  fi
  total_tests=$((total_tests + 1))
done
total_failed=$((total_tests - successful_tests))
echo "All tests completed." | tee -a $LOG_FILE
echo "failed test: $total_failed  " | tee -a $LOG_FILE
echo "Total tests run: $total_tests" | tee -a $LOG_FILE
