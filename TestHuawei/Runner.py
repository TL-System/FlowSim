

import os
import sys
import getopt


def main(args):
#    routing_scheme = ""
#    opts, args = getopt.getopt(args[1:], "r:", ["routing="])
#    for o, a in opts:
#        if o in ("-r","--routing"):
#            routing_scheme = a
#    if routing_scheme != "":
#        os.system("python TestSimulator.py -r " + routing_scheme)
#    else:
     for i in range(1, len(sys.argv)):
         sys.argv[i] =" " + sys.argv[i]
     #print ''.join(sys.argv[1:])
     os.system("python TestSimulator.py" + ''.join(sys.argv[1:]))

if __name__ == '__main__':
    main(sys.argv)
