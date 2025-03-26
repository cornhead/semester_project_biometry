import random
import json
from operator import mul


class Testpattern:
    def __init__(self, n, m):
        self.model = Testpattern._generate_bit_vector(n, 0.5)
        self.patterns = [ Testpattern._generate_bit_vector(n, (i+1)/(m+1)) for i in range(m) ]

        self.miura = [ Testpattern._miura(self.model, pattern) for pattern in self.patterns ]

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

if __name__ == '__main__':
    testcase = Testpattern(16, 10)
    print(testcase.toJSON())
