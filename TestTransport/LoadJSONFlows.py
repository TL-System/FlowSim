__author__ = 'li'
import json
from pprint import pprint

with open('Out/flow10.json') as inputf:
    tempflows = json.load(inputf)

pprint(tempflows['1']['deadline'])
print len(tempflows)

for i in range(len(tempflows)):
    print tempflows['{}'.format(i)]['deadline']
    print tempflows['{}'.format(i)]