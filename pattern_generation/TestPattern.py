import random
import json
import numpy as np

from operator import mul

class TestPattern:
    '''
    This class is used to generate and represent test patterns. It contains one
    model and many probes and their respective miura scores. That is, one test
    pattern contains many test cases.

    Initializes a test pattern by filling it with random bits.

    The `model` is always filled with a vector that is distributed as Bernoulli(0.5)

    The individual `probes` are also Bernoulli distributed, but the a probability
    that gradually increases from 0 to 1.

    The `miura` property is an array containing all the Miura scores between
    the model and the (many) probes.

    The `convolution` property contains the convolutions between the model and
    the probes, where the order of the entries in the model are reversed.
    Effectively, this gives us vectors containing the inner products between the
    model and probes for all possible offsets. (See project report for detaisl).
    This property is enforced with assertions.

    :param n: Length of the vectors
    :param m: Number of probes (i.e. test cases)
    '''

    def __init__(self, n:int, m:int):
        self.model = TestPattern._generate_bit_vector(n, 0.5)
        self.probes = [ TestPattern._generate_bit_vector(n, (i+1)/(m+1)) for i in range(m) ]

        self.miura = [ TestPattern._miura(self.model, probe) for probe in self.probes]
        self.convolutions = [ np.convolve(self.model[::-1], p) for p in self.probes] # convolve with reversed model
        self.convolutions = [ [int(x) for x in c] + [0] for c in self.convolutions] # need to convert to int and append zero to match length of output of circuit

        # test that the convolution actually matches the inner products:
        for p,c in zip(self.probes, self.convolutions):
            # print("probe:", p)
            # print("model:", self.model)
            # print("conv: ", c)
            for i in range(len(c)):
                inner_product = sum([ p[j+i-n+1]*self.model[j] for j in range(len(p)) if j+i-n+1>=0 and j+i-n+1<n])
                # print(inner_product)
                assert inner_product == c[i]

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

    def __str__(self):
        return json.dumps(self.__dict__)
