'''
A generator for test patterns and random circuit input for the semester project on biometric finger vein recognition
'''

import sys

from CircuitInput import *
from TestPattern import *

def usage() -> None:
    '''
    Prints the usage message and terminates the process with exit code 0.

    :returns: Termination with exit code 0
    '''

    with open('usage.txt', 'r') as f:
        print(f.read())

    sys.exit(0)

def parse_cli_args(argv:list[str]) -> tuple[str, tuple]:
    '''
    Parses the command-line arguments

    The returned tuple indicates the command that is to be executed
    together with its arguments/parameters.

    The possible values for the returned command string are:
        - usage
        - die
        - test_pattern
        - random_input

    Note that the set of possible return values for the command differs
    from the set of accepted input values for the command over the CLI.

    :param argv: Array of the command-line arguments(e.g. obtainend from `sys.argv()`)
    :return: A tuple of a string-identifier of the command and a tuple of arguments
    '''

    argc = len(argv)

    if argc < 2:
        return("usage", ())

    command_str = argv[1]

    match command_str:
        case "test_pattern":
            if argc < 3 or argc > 4:
                return ("die", (f"Error: The command \"test_pattern\" takes 1 or 2 arguments, {argc-2} given."))

            try:
                vector_length = int(argv[2])
            except ValueError:
                return ("die", ("Error: Argument vector_length needs to be an integer"))

            if argc == 4:
                try:
                    n_test_cases = int(argv[3])
                except ValueError:
                    return ("die", ("Error: If N_test_cases is spedified, it needs to be an integer, otherwise, 10 will be used as default value."))
            else:
                n_test_cases = 10

            return ("test_pattern", (vector_length, n_test_cases))

        case "random_input":
            if argc != 3:
                return ("die", (f"Error: The command \"random_input\" takes 1 argument, {argc-2} given."))

            try:
                vector_length = int(argv[2])
            except ValueError:
                return ("die", ("Error: Argument vector_length needs to be an integer"))

            return ("random_input", (vector_length))

        case "help":
            return("usage", ())

        case _:
            return ("die", ("Error: unrecognized command \"" + command_str + "\""))


if __name__ == '__main__':
    (command, args) = parse_cli_args(sys.argv)

    stdout = sys.stdout

    match command:
        case "usage":
            usage()
        case "die":
            print(args, file=sys.stderr)
            sys.exit(1)
        case "test_pattern":
            testcase = TestPattern(*args)
            stdout.write(str(testcase))
            stdout.write('\n')
        case "random_input":
            myinput = CircuitInput(args)
            stdout.write(str(myinput))
            stdout.write('\n')

        case _:
            print(
                "Ooops, this should not happen.\n"
                "The program tried to call an unimplemented command.\n"
                "Please contact the author." \
            , file=sys.stderr)
            sys.exit(1)
