__author__ = 'li'

import csv

fname = 'fct-all.csv'
rname = 'trace.csv'

f = open(fname, "rw")
r = open(rname, "r")
writer = csv.writer(f)

cf = f.readlines()
cr = r.readlines()
for l in cr:
    pass

for l in cr:
    fid, m, h, e = l.split(',')


f.close()
r.close()

