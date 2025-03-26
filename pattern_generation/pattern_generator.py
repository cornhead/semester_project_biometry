import random
import json
from operator import mul
import sys

def usage():
    '''
    Prints the usage message and terminates the process with exit code 0.
    '''

    print("Usage: pattern_generator.py <vector_length> [N_test_cases]")
    print()
    print("Produces a so-called test pattern for vectors of length vector_length.")
    print("One model will be created and N_test_cases probes.")
    print("If the N_test_cases parameter is not specified, 10 will be used as default value.")
    sys.exit(0)

def parse_cli_args(argv):
    '''
    Takes an arry of command-line interface parameters (e.g. from sys.argv) and
    parses them. If an error occurs, an error message and the usage message
    are printed.

    The function returns a tuple containing the vector_length and n_test_cases
    parameters.
    '''

    argc = len(argv)

    if argc < 2 or argc > 3:
        usage()

    try:
        vector_length = int(argv[1])
    except ValueError:
        print("Error: Argument vector_length needs to be an integer\n")
        usage()

    if argc == 3:
        try:
            n_test_cases = int(argv[2])
        except ValueError:
            print("Error: If N_test_cases is spedified, it needs to be an integer, otherwise, 10 will be used as default value.\n")
            usage()
    else:
        n_test_cases = 10

    return (vector_length, n_test_cases)


class Testpattern:
    def __init__(self, n, m):
        self.model = Testpattern._generate_bit_vector(n, 0.5)
        self.probes = [ Testpattern._generate_bit_vector(n, (i+1)/(m+1)) for i in range(m) ]

        self.miura = [ Testpattern._miura(self.model, probe) for probe in self.probes]

    '''
        @brief: generates a bit vector of length n where each element is distributed Bernoulli(p)
    '''
    def _generate_bit_vector(n, p):
        return [ int(random.random() <= p) for _ in range(n)]

    def _miura(a, b):
        dot = lambda a, b: sum(map(mul, a, b))
        return dot(a,b)/(dot(a,a) + dot(b,b))

    def toJSON(self):
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.toJSON()

if __name__ == '__main__':
    (vector_length, n_test_cases) = parse_cli_args(sys.argv)
    testcase = Testpattern(vector_length, n_test_cases)
    print(testcase)
