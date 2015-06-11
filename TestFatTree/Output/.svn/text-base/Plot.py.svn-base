__author__ = 'zm'

import Gnuplot, Gnuplot.funcutils
import getopt, sys

# The port number of each switch in fat-tree topology
K = 8

opts, args = getopt.getopt(sys.argv[1:], "K:", ["K=",])
for o, a in opts:
    if o in ("-K", "--K"):
        K = int(a)

Xrange=1100
Yrange=105

g = Gnuplot.Gnuplot(debug=1)

g("set autoscale")
g("set xlabel \"Throughput (Mbps)\" font \", 20\" offset 0, -0.5")
g("set ylabel \"CDF (%)\" font \", 20\"")
g("set xrange [0 : %d]" % Xrange)
g("set yrange [0 : %d]" % Yrange)
g("set ytics font \", 20\"")
g("set xtics font \", 20\"")
g("set key box right bottom")
g("set key spacing 4.0 nobox right bottom font \",25\"")
g("set term postscript color enhanced solid")
g("set title \"K=%d, 100MB, {/Symbol l}=100\" font \", 20\"" % K)
g("set output \"cdf_K%d_cmp.eps\"" % K)
g("plot \"K%d_S100_L100_a0.8_plot.dat\" using 1:($2 * 100) title \"CCDN\"w linespoint pointtype 4 lt rgb \"red\" lw 2.5,"
  "\"K%d_S100_L100_a0.9_plot.dat\" using 1:($2 * 100) title \"HDFS\"w linespoint pointtype 6 lt rgb \"blue\" lw 2.5,"
  "\"K%d_S100_L100_a1.0_plot.dat\" using 1:($2 * 100) title \"HDFS+Cache\"w linespoint pointtype 8 lt rgb \"green\" lw 2.5"
  % (K, K, K))
"""
g("set title \"K=%d, 100MB, a=5\" font \", 20\"" % K)
g("set output \"cdf_K%d_L.eps\"" % K)
g("plot \"K%d_S100_L100_a5_plot.dat\" using 1:($2 * 100) title \"L100\"w linespoint pointtype 4 lt rgb \"red\" lw 2.5,"
  "\"K%d_S100_L300_a5_plot.dat\" using 1:($2 * 100) title \"L300\"w linespoint pointtype 6 lt rgb \"blue\" lw 2.5,"
  "\"K%d_S100_L500_a5_plot.dat\" using 1:($2 * 100) title \"L500\"w linespoint pointtype 8 lt rgb \"green\" lw 2.5"
  % (K, K, K))
"""
