__author__ = 'lich'

import os

for K in [8, 12, 16, 24]:
    for mean in [10, 100, 300, 500]:
        for a in [1, 5, 10]:
            os.system("python GenFlowInput.py -K %d -S 100 -L %d -a %d" % (K, mean, a))
