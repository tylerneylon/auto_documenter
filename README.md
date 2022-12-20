# add_docstrings

This is a little script that uses gpt to add docstrings to Python code.

The current code is a work in progress. Version 1 adds a docstring to all
function and method definitions. If you happen to already have a docstring on a
function, you'll end up with two.

Usage:

    ./add_docstrings.py <my_code.py>

This prints output to a new file (or stdout) and does not edit the original file. This way you
can run a diff and see if you like the changes.

Configuration:
    Choose whether you want to print to console or file: "print_to_file" to true if, instead of printing the modified code to the console, you'd like it printed to a new file in the output directory
    Make mock calls to GPT? Set "mock_calls" to true if, instead of making calls to GPT, you'd like to make only simulated calls. (This is useful for testing this codebase without hitting API limits)