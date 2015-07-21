__author__ = 'li'

import csv

reader = csv.reader(open("mcp.csv", "rb"))
mcp = list(reader)

reader = csv.reader(open("d2tcp.csv", "rb"))
d2tcp = list(reader)
# for i in range(len(d2tcp[0])):
#     d2tcp[0][i] = 'd2tcp_' + d2tcp[0][i]

reader = csv.reader(open("dctcp.csv", "rb"))
dctcp = list(reader)
# for i in range(len(dctcp[0])):
#     dctcp[0][i] = 'dctcp_' + dctcp[0][i]

reader = csv.reader(open("tcp.csv", "rb"))
tcp = list(reader)
# for i in range(len(tcp[0])):
#     tcp[0][i] = 'tcp_' + tcp[0][i]

result = [a+b+c+d for (a, b, c, d) in zip(mcp, d2tcp, dctcp, tcp)]

writer = csv.writer(open("all.csv", "wb"))
writer.writerows(result)