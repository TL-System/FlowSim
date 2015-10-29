__author__ = 'li'

import json

from StepByStepSimulator import *

sim = StepByStepSimulator(
    concurrency=5,
    simtime=0.01,
    rtt=0.000001 * 100)
flows = sim.geninput()

flowdict = dict()
for f in flows:
    flowdict[f.flowId] = {
        'flowSize': f.flowSize,
        'deadline': f.deadline,
        'startTime': f.startTime,
        'finishTime': f.finishTime,
    }

with open('Out/flowdump.json', 'wb') as f:
    flowdump = json.dump(flowdict, f)

print json.dumps(flowdict, sort_keys=True, indent=4, separators=(',', ': '))

# TODO: next step is to creaate a small scenario with only 10 or less flows to get a good example for mcp
