'''
:synopsis: Prompt users for information


.. moduleauthor: Paul Diaconescu <p@afajl.com>
'''
import re

try:
    import readline
    has_readline = True
except ImportError:
    has_readline = False
    pass

def _indent_out(question):
    indent = 0
    for c in question:
        if c != ' ':
            break
        indent += 1

    def out(msg, to_s=False):
        s = ' '*indent + msg
        if to_s:
            return s
        else:
            print s
    return out
 

def _to_type(answer, type):
    ''' Tries to convert the answer to the desired type '''
    if type is None:
        # Dont convert
        return answer, None
    if type is int:
        try:
            return type(answer), None
        except ValueError:
            return None, 'Answer must be a integer'
    if type is float:
        try:
            return type(answer), None
        except ValueError:
            return None, 'Answer must be a float'
    if type is bool:
        if answer[0] in ('y', 'Y', 't', 'j'):
            return True, None
        elif answer[0] in ('n', 'N', 'f'):
            return False, None
        else:
            return None, 'Answer yes or no'
    else:
        return type(answer)
     
    return type(answer), None

def _run_checks(answer, checks):
    ''' Runs checks, (func, help) on answer '''
    error = None
    for test, help in checks:
        if isinstance(test, str):
            match = re.match(test, answer)
            if not match:
                error = help
                break
        if hasattr(test, 'match'):
            match = test.match(answer)
            if not match:
                error = help
                break
        if hasattr(test, '__call__'):
            if not test(answer):
                error = help
                break
    return error


def ask(question, default='', type=None, checks=()): 
    ''' Ask user a question

    :arg question: Question to prompt for. Leading spaces will set the
                   indent level for the error responses.
    :arg default:  The default answer as a string.
    :arg type:     Python type the answer must have. Answers are converted
                   to the requested type before checks are run. Support for
                   str, int, float and bool are built in. 
                   
                   If you supply your own function it must take a string as
                   argument and return a tuple where the first value is the
                   converted answer or None if if failed. If it fails the
                   second value is the error message displayd to the user,
                   example::

                        def int_list(answer):
                            try:
                                ints = [int(i) for i in answer.split(',')]
                                # Success!
                                return ints, None
                            except ValueError: 
                                # Fail!
                                return None, 'You must supply a list of integers'

                        sy.prompt.ask('Give me a intlist: ', type=int_list)

                        Give me a intlist: 1, 2, 3
                        [1, 2, 3]


    :arg checks:   List of checks in the form ``[(check, errormsg), (check, ...)]``.
                   The check can be a regular expression string, a compiled 
                   pattern or a function. The function must take a string as 
                   argument and return True if the check passes.  If the check 
                   fails the errormsg is printed to the user.

    '''
    assert isinstance(default, str), 'Default must be a string'

    # Get a print_error function that correctly indents 
    # the error message
    print_error = _indent_out(question)

    while True:
        answer = raw_input(question).strip()
        if not answer:
            if default:
                answer = default
            else:
                # ask again
                continue

        converted = answer
        if type:
            converted, error = _to_type(answer, type)
            if error:
                print_error(error)
                continue

        if checks:
            error = _run_checks(converted, checks)
            if error:
                print_error(error)
                continue

        return converted

        
def confirm(question, default=''):
    ''' Ask a yes or no question
    
    :arg default: True or False
    :returns: Boolean answer
    '''
    if default is True:
        default='y'
    elif default is False:
        default='n'

    return ask(question,                
               default=default,
               type=bool)


def choose(question, choices, multichoice=False, default=''):
    ''' Let user select one or more items from a list

    Presents user with the question and the list of choices. Returns the index
    of the choice selected. If ``multichoice``
    is true the user can pick more then one choice and a list of indexes are 
    returned::

        choice = sy.prompt.choose('Pick one:', ['a', 'b', 'c'])
        # Pick one:
        #  1) a
        #  2) b
        #  3) c
        # Choice: 1

        print choice
        0

        choices = sy.prompt.choose('Pick one or more:', ['a', 'b', 'c'], 
                                    mutlichoice=True)
        # Pick one or more:
        #  1) a
        #  2) b
        #  3) c
        # Choices: 1, 3

        print choices
        [0,2]
 
    :arg question: Question to print before list of choices
    :arg choices:  List of choices. If the choice is not a string an attempt to 
                   convert it to a string with :func:`str()` is made. 
    :arg multichoice: If True the user can pick multiple choices, separated by
                      commas. The return value will be a list of indexes in the
                      choices list that the user picked.
    :arg default: Default choice as a string the user would have written, ex:
                  ``"1,2"``.
    '''

    out = _indent_out(question)

    print question
    for i, choice in enumerate(choices):
        out( '%d) %s' % (i+1, str(choice)) )
    print
 
    if multichoice:
        choice_q = 'Choices: '
    else:
        choice_q = 'Choice: '

    def to_index_list(answer):
        try:
            ints = [int(i) - 1 for i in re.split(r'\s*,\s*|\s+', answer)]  
            for i in ints:
                if i < 0 or i >= len(choices):
                    return None, '%d is not a valid option' % (i + 1)
            return ints, None
        except ValueError:
            return None, 'You must use numbers'
            
    while True:
        selected = ask(out(choice_q, to_s=True), type=to_index_list, 
                         default=default)
        if selected:
            if not multichoice:
                if len(selected) > 1:
                    out('Select one value')
                    continue
                return selected[0]
            else:
                return selected


