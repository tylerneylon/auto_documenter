#!/usr/bin/env python3
"""
    add_docstrings.py

    Usage:
        add_docstrings.py <my_code.py>

    NOTE: This requires Python 3.9+ (this is openai's library requirement).

    This app is a work in progress.
    The long-term plan is to add docstrings to the functions and classes in the
    file `my_code.py` provided on the command line.

    Currently the modified file is printed to stdout.
    This finds all function and method definitions in the input file and adds a
    docstring for them. This currently assumes there are no docstrings for such
    definitions. If there are already docstrings, then you will end up with the
    new, gpt-based docstring on top of the old docstring.

    The wishlist / todo ideas below clarify more about what the current v1
    script does _not_ do. :)
"""

# TODO Ideas:
#
#  * Work nicely with existing docstrings (use as input and overwrite).
#  * Add docstrings for class definitions.
#  * Add top-of-file docstrings.
#  * Detect indentation type per file.
#  * Wrap long lines at detected file width (or command-line param).
#  * We could add per-line or per-code-paragraph comments.


# ______________________________________________________________________
# Imports

# The openai library is slow to load, so be clear something is happening.
print('Loading libraries .. ', end='', flush=True)

# Standard library imports.
import json
import os
import random
import re
import sys
import time
from pathlib import Path

# Third party imports.
import openai

print('done!')


# ______________________________________________________________________
# Constants and globals

NUM_REPLY_TOKENS = 700


# Turn this on to have additional debug output written to a file.
if False:
    dbg_f = open('dbg_out.txt', 'w')
else:
    dbg_f = None


# ______________________________________________________________________
# Debug functions

def pr(s=''):
    global dbg_f
    if dbg_f:
        print(s, file=dbg_f)


# ______________________________________________________________________
# GPT functions

def send_prompt(prompt):

    pr('\n' + ('_' * 70))
    pr('send_prompt()')
    pr(f'I will send over this prompt:\n\n')
    pr(prompt)

    return openai.Completion.create(
        model = "text-davinci-003",
        prompt = prompt,
        temperature = 0,
        max_tokens = NUM_REPLY_TOKENS,
        top_p = 1.0,
        frequency_penalty = 0.0,
        presence_penalty = 0.0
    )

def print_fn_w_docstring(code_str):
    
    prompt  = 'Write a docstring for the following code:\n\n'
    prompt += code_str
    prompt += '\n\nDocstring:\n"""'

    response = send_prompt(prompt)
    answer   = response['choices'][0]['text']
    answer   = '"""' + answer

    pr('Got the answer:\n')
    pr(answer)

    code_lines = code_str.split('\n')
    print(code_lines[0])

    indent = re.search(r'^(\s*)', code_lines[0])
    indent = len(indent.group(1))
    prefix = ' ' * (indent + 4)

    for ans_line in answer.split('\n'):
        print(prefix + ans_line)

    for line in code_lines[1:]:
        print(line)


# ______________________________________________________________________
# Main

if __name__ == '__main__':

    keyfile = Path('config.json')
    if not keyfile.is_file():
        print('Error: Please add your openai api key to the file config.json')
        print('The format is {"api_key": "your_key"}')
        sys.exit(0)
    
    with keyfile.open() as f:
        openai.api_key = json.load(f)['api_key']

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    with open(sys.argv[1]) as f:
        code = f.read()
    lines = code.split('\n')

    capture_mode = False
    indentation  = 0
    current_fn   = None
    for line in lines:
        if m := re.search(r'^(\s*)def ', line):
            capture_mode = True
            indentation  = len(m.group(1))
            current_fn   = [line]  # This will be a list of lines.
        else:
            this_indent = re.search(r'^(\s*)', line)
            this_indent = len(this_indent.group(1))
            if len(line.strip()) > 0 and this_indent <= indentation:
                if capture_mode:
                    # We just finished capturing a function definition.
                    capture_mode = False
                    print_fn_w_docstring('\n'.join(current_fn))
            if capture_mode:
                current_fn.append(line)
            else:
                print(line)
