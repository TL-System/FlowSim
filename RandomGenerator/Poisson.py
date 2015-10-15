__author__ = 'lich'

import random, math

class PoissonRand:
    """
    This is used to generate poisson numbers.
    The user needs to input the lambda, which is the expected value of poisson distribution.
    It is also the average arrival rate in unit time. For example, the mean number of events happens in a second.
    Since the delta time between two events follows the exponential distribution, means that:
    P{events happens after delta_t} = 1 - e ^ (lambda * delta_t)
    Thus, we random generate a P in (0, 1) and calculate the delta_t by the equation above.
    Note that if P is extremely small, for example, P = 0, that leads to an infinite delta_t, therefore, we needs to set a bound.
    """
    def __init__(self, mean, bound):
        self.mean = mean
        self.bound = bound

    def GetPoissonNumber(self):
        r = random.random()
        p = math.log(1 - r) / self.mean * (-1)
        if p > self.bound:
            p = self.bound
        return p

    def __del__(self):
        pass
