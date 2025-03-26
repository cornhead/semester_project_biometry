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

    print("Usage: pattern_generator.py <vector_length> [N_test_cases]")
    print()
    print("Produces a so-called test pattern for vectors of length vector_length.")
    print("One model will be created and N_test_cases probes.")
    print("If the N_test_cases parameter is not specified, 10 will be used as default value.")
    sys.exit(0)

def parse_cli_args(argv:list[str]) -> tuple[int, int]:
    '''
    Parses the command-line arguments

    :param argv: Array of the command-line arguments(e.g. obtainend from `sys.argv()`)
    :return: A tuple with `vector_length` and `n_test_cases`
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
    (vector_length, n_test_cases) = parse_cli_args(sys.argv)
    testcase = Testpattern(vector_length, n_test_cases)
    print(testcase)
