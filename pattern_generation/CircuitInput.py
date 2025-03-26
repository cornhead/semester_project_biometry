import random
import json

from TestPattern import *

class CircuitInput:
    '''
    This class is used to generate and represent input to the SNARK circuit.
    This is somewhat different from a test case, as it also includes the randomness
    for the commitment, but not the expected Miura score.

    :param n: Vector length
    '''
    def __init__(self, n:int):
        pattern = TestPattern(n, 1)

        self.model = pattern.model
        self.probe = pattern.probes[0]
        self.r_model = CircuitInput._random_field_element()
        self.r_probe = CircuitInput._random_field_element()

    def _random_field_element():
        '''
        Generate a random element of the finite field over the BN128 elliptic curve.

        :important: As this is only a Proof of Concept, we do not use "good" randomness. Do not use the `random` library in deployed cryptographic implementations!
        '''
        bn128_p = 21888242871839275222246405745257275088548364400416034343698204186575808495617; # order of the bn128 curve
        return random.randrange(0, bn128_p)

    def __str__(self):
        return json.dumps(self.__dict__)
