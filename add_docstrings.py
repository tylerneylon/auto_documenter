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


# KNOWN BUGS:
#  * When there are back to back function definitions, this script will throw out all but the last.


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
MOCK_CALLS = False


# Turn this on to have additional debug output written to a file.
if True:
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

def send_prompt_to_gpt(prompt):
    """
    This function sends the provided prompt to GPT and returns GPT's response.
    """

    # Document what's happening to the debugger output file
    pr('\n' + ('_' * 70))
    pr('send_prompt()')
    pr(f'I will send over this prompt:\n\n')
    pr(prompt)

    if MOCK_CALLS:
        gpt_response = "\nTHIS IS A MOCK DOCSTRING. Set MOCK_CALLS to False to get real ones.\n\"\"\""
    else:
        # Send request to GPT, return response
        response = openai.Completion.create(
            model = "text-davinci-003",
            prompt = prompt,
            temperature = 0,
            max_tokens = NUM_REPLY_TOKENS,
            top_p = 1.0,
            frequency_penalty = 0.0,
            presence_penalty = 0.0
        )
        gpt_response =  response['choices'][0]['text']

    return "\"\"\"" + gpt_response


def fetch_docstring(code_str):

    # Construct the GPT prompt
    prompt  = 'Write a docstring for the following code:\n\n'
    prompt += code_str
    prompt += '\n\nDocstring:\n"""'

    # Make the request for docstring to GPT
    docstring = send_prompt_to_gpt(prompt)

    # Document what's happening to the debugger output file
    pr('Got the docstring:\n')
    pr(docstring)

    # Return it
    return docstring


def print_fn_w_docstring(code_str):
    """
    This function requests GPT provide a docstring for the stringified function provided as an argument.
    It then prints the stringified function with the docstring added.
    """

    # Fetch the docstring
    docstring = fetch_docstring(code_str)

    # Print the function header/signature
    code_lines = code_str.split('\n')
    print(code_lines[0])

    # Print the docstring
    indent = re.search(r'^(\s*)', code_lines[0])
    indent = len(indent.group(1))
    prefix = ' ' * (indent + 4)

    for ans_line in docstring.split('\n'):
        print(prefix + ans_line)

    # Print the rest of the function
    for line in code_lines[1:]:
        print(line)


# ______________________________________________________________________
# Main

if __name__ == '__main__':

    # Verify OpenAI API key is configured
    keyfile = Path('config.json')
    if not keyfile.is_file():
        print('Error: Please add your openai api key to the file config.json')
        print('The format is {"api_key": "your_key"}')
        sys.exit(0)
    
    with keyfile.open() as f:
        openai.api_key = json.load(f)['api_key']

    # If this script has been improperly executed, print the docs
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    # Open and ingest the python file provided as an input
    with open(sys.argv[1]) as f:
        code = f.read()
    lines = code.split('\n')


    print('Here is your code with docstrings added: \n\n')


    # Get 'Top of File' docstring
    tof_docstring = fetch_docstring(code)


    # Get Function docstring
    #       Walk through the input code, line-by-line.
    #       Print out code, until you find a function. 
    #       When you find a function, capture it and have GPT provide a docstring for it.
    #       Print out the function with docstring.
    #       Continue as before until file end.

    passed_the_shebang_line = False
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
                if not passed_the_shebang_line and re.search(r'^#!', line):
                    passed_the_shebang_line = True
                    print(line)
                    print(tof_docstring)
                else:
                    print(line)
