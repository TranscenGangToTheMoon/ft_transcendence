#!/bin/bash

if [ -d "tests" ]; then
    BASE=.
else
    BASE=./API-unittest
fi

TESTS_FOLDER=$BASE/tests/
echo "Running tests in $TESTS_FOLDER"
python -m unittest discover -s $TESTS_FOLDER -p "test_*.py"
