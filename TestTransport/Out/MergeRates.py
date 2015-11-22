__author__ = 'li'

import csv

reader = csv.reader(open("mcp_rates.csv", "rb"))
mcp = list(reader)

reader = csv.reader(open("d2tcp_rates.csv", "rb"))
d2tcp = list(reader)
# for i in range(len(d2tcp[0])):
#     d2tcp[0][i] = 'd2tcp_' + d2tcp[0][i]

reader = csv.reader(open("dctcp_rates.csv", "rb"))
dctcp = list(reader)
# for i in range(len(dctcp[0])):
#     dctcp[0][i] = 'dctcp_' + dctcp[0][i]

reader = csv.reader(open("tcp_rates.csv", "rb"))
tcp = list(reader)
# for i in range(len(tcp[0])):
#     tcp[0][i] = 'tcp_' + tcp[0][i]

# result = [[a,b,c,d] for (a, b, c, d) in zip(mcp, d2tcp, dctcp, tcp)]
result = zip(mcp[0], d2tcp[0], dctcp[0], tcp[0])

writer = csv.writer(open("all_rates.csv", "wb"))
writer.writerow(['mcp', 'd2tcp', 'dctcp', 'tcp'])
for r in result:
    writer.writerow(r)