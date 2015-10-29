__author__ = 'li'

import random


def weighted_choice(choices):
    total = sum([choices[c] for c in choices])
    r = random.uniform(0, total)
    upto = 0
    for c in choices:
        if upto + choices[c] > r:
            return c
        upto += choices[c]
    assert False, "Shouldn't get here"


# Usage example
if __name__ == "__main__":
    choice = ['a', 'b', 'c', 'd']
    weight = [1, 2, 3, 4]
    css = dict(zip(choice, weight))
    for i in range(10):
        print weighted_choice(css)
