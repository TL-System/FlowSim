import sys
import csv
import math

for line in sys.stdin:
    l = line.rstrip('\r\n').split(',')
    repeat_number = int(math.ceil(1.0/float(l[6])))
   # print repeat_number
    for i in range(repeat_number*8):
        print line.rstrip('\r\n')

