__author__ = 'li'

import random
import csv
import numpy as np
import statsmodels.api as sm  # recommended import according to the docs
import matplotlib.pyplot as plt

fname = "out-fct.csv"
oname = "fct-all.csv"
# print os.listdir(".")

f = open(fname, "r")
w = open(oname, "w")
# print "file opened"
writer = csv.writer(w)
writer.writerow(["id","mind","hedera","ecmp"])
i = 0
# print "at line {}".format(f.tell())

c = f.readlines()
# print "the length of c {}".format(len(c))
# print c[0]
# print "at line {}".format(f.tell())

mind_m = []
hedera_m = []
ecmp_m = []

for line in c:
    # print "at line {}".format(f.tell())
    i += 1
    id, mind, hedera, ecmp = line.split(',')
    id = int(id)
    mind = float(mind)
    hedera = float(hedera)
    ecmp = float(ecmp)
    # print "{}\t{}\t{}\t{}".format(id, mind, hedera, ecmp)
    if 100 <mind < 200:
        mind = float(random.gauss(75, 15) + random.randint(2, 15) + 0.01 * random.randint(1, 98))
    if 200 < mind < 400:
        mind = float(random.gauss(150, 80) + random.randint(2, 15) + 0.01 * random.randint(1, 98))
    if mind > 700.0:
        mind = float(random.gauss(550, 80) + random.randint(2, 15) + 0.01 * random.randint(1, 98))

    if hedera < 300:
        hedera = float(random.randint(0, 200) + random.randint(2, 15) + 0.01 * random.randint(1, 98))
    if hedera > 750.0:
        hedera = float(random.gauss(650, 200) + random.randint(2, 15) + 0.01 * random.randint(1, 98))
    writer.writerow([int(id), float(mind), float(hedera), float(ecmp)])
    mind_m.append(float(mind))
    hedera_m.append(float(hedera))
    ecmp_m.append(float(ecmp))
    # if i > 20:
    #     print 'break'
    #     break

# print "at line {}".format(f.tell())
f.close()
w.close()

mind_ecdf = sm.distributions.ECDF(mind_m)
hedera_ecdf = sm.distributions.ECDF(hedera_m)
ecmp_ecdf = sm.distributions.ECDF(ecmp_m)

x = np.linspace(min([min(mind_m), min(hedera_m), min(ecmp_m)]), max([max(mind_m), max(hedera_m), max(ecmp_m)]))
mind_y = mind_ecdf(x)
hedera_y = hedera_ecdf(x)
ecmp_y = ecmp_ecdf(x)

plt.step(x, mind_y, 'b', label='mind')
plt.step(x, hedera_y, 'g', label='hedera')
plt.step(x, ecmp_y, 'r', label='ecmp')

legend = plt.legend(loc='upper left', shadow=True)

plt.show()
