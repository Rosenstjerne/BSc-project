#!/bin/bash

# This script runs all the tests in the parserTest directory, compares the output to the existing .out files, and logs the results
COMPILER_COMMAND="python ../src/compiler.py -s -i"
PARSER_TEST_DIR="./parserTest"

# Get all the test files
TEST_FILES=$(find $PARSER_TEST_DIR -name "*.leif")

# Set the log file name
LOG_FILE="testLog.txt"
echo "" > $LOG_FILE

# Initialize counters for total tests and successful tests
total_tests=0
successful_tests=0

# Iterate through the test files, run them with the compiler, and compare the results with the existing .out files
for file in $TEST_FILES; do
  echo "Running test: $file" | tee -a $LOG_FILE
  # Replace the file extension .leif with .out and .tmp
  out_file="${file%.leif}.out"
  tmp_file="${file%.leif}.tmp"
  # Run the compiler command, redirecting stdout to the .tmp file and stderr to the log file
  $COMPILER_COMMAND $file > $tmp_file 2>> $LOG_FILE

  # Compare the .tmp file with the .out file using the diff command
  if diff -q $tmp_file $out_file &>/dev/null; then
    successful_tests=$((successful_tests + 1))
    echo "Test passed" | tee -a $LOG_FILE
  else
    echo "Test failed" | tee -a $LOG_FILE
  fi

  # Remove the .tmp file
  rm $tmp_file
  total_tests=$((total_tests + 1))
done
total_failed=$((total_tests - successful_tests))
echo "All tests completed." | tee -a $LOG_FILE
echo "Failed tests: $total_failed" | tee -a $LOG_FILE
echo "Total tests run: $total_tests" | tee -a $LOG_FILE