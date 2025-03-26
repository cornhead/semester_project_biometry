'''
A generator for test patterns for the semester project on biometric finger vein recognition

:moduleauthor: Konrad Klier <konrad.klier@epfl.ch>
'''

import random
import json
from operator import mul
import sys

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

    :param argv: Array of the command-line arguments(e.g. obtainend from `sys.argv()`)
    :return: A tuple with `vector_length` and `n_test_cases`
    '''

    argc = len(argv)

    if argc < 2:
        return("usage", ())

    command_str = argv[1]

    match command_str:
        case "pattern":
            if argc < 3 or argc > 4:
                return ("die", (f"Error: The command \"pattern\" takes 1 or 2 arguments, {argc-2} given."))

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

            return ("pattern", (vector_length, n_test_cases))

        case "help":
            return("usage", ())

        case _:
            return ("die", ("Error: unrecognized command \"" + command_str + "\""))


class Testpattern:
    '''
    This class is used to generate and represent test patterns. It contains one
    model and many probes and their respective miura scores. That is, one test
    pattern contains many test cases.

    Initializes a test pattern by filling it with random bits.

    The `model` is always filled with a vector that is distributed as Bernoulli(0.5)

    The individual `probes` are also Bernoulli distributed, but the a probability
    that gradually increases from 0 to 1.

    :param n: Length of the vectors
    :param m: Number of probes (i.e. test cases)
    '''

    def __init__(self, n:int, m:int):
        self.model = Testpattern._generate_bit_vector(n, 0.5)
        self.probes = [ Testpattern._generate_bit_vector(n, (i+1)/(m+1)) for i in range(m) ]

        self.miura = [ Testpattern._miura(self.model, probe) for probe in self.probes]

    def _generate_bit_vector(n:int, p:float) -> list[int]:
        '''
        Generates random bit vectors where each element is distributed Bernoulli(p)

        :param n: Vector length
        :param p: Probability for Bernoulli distribution
        :return: A Bernoulli(`p`) distributed vector of `n` bits
        '''
        return [ int(random.random() <= p) for _ in range(n)]

    def _miura(a:list[int], b:list[int]) -> float:
        '''
        Computes the Miura score between two vectors

        :param a: First vector
        :param b: second vector
        :return: The Miura score between `a` and `b`
        '''

        assert len(a) == len(b)

        dot = lambda a, b: sum(map(mul, a, b))
        return dot(a,b)/(dot(a,a) + dot(b,b))

    def toJSON(self):
        '''
        Turns an instance of the class into a JSON string
        '''
        return json.dumps(self.__dict__)

    def __str__(self):
        return self.toJSON()

if __name__ == '__main__':
    (command, args) = parse_cli_args(sys.argv)

    match command:
        case "usage":
            usage()
        case "die":
            print(args, file=sys.stderr)
        case "pattern":
            testcase = Testpattern(*args)
            print(testcase)
