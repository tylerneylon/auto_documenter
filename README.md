# add_docstrings

This is a little script that uses gpt to add docstrings to Python code.

The current code is a work in progress. Version 1 adds a docstring to all
function and method definitions. If you happen to already have a docstring on a
function, you'll end up with two.

Usage:

    ./add_docstrings.py <my_code.py>

This prints output to stdout and does not edit the original file. This way you
can run a diff and see if you like the changes.
