#! /usr/bin/gnuplot
Xrange=1100
Yrange=105

set autoscale
set xlabel "Throughput (Mbps)" font ", 30" offset 0, -1.0
set ylabel "CDF (%)" font ", 30"
set xrange [0 : Xrange]
set yrange [0 : Yrange]
set ytics font ", 30"
set xtics font ", 30"
#set xtics ("200" 200, "400" 400, "600" 600, "800" 800, "1200" 1200, "1600" 1600, "2000" 2000) font ",30" offset 0, -0.5
#set title "100 Flows, 1MB per flow, {/Symbol l}=50" font ", 20"
set key box right bottom
set term postscript color enhanced solid
set output "cdf.eps"
set key spacing 4.0 nobox right bottom font ",35"
plot "plot_K24.txt" using 1:($2 * 100) title "ECMP"w linespoint lt rgb "red" lw 2.5