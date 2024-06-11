#!/bin/bash

gcc shuffle.c -o shuffle
# Outer loop
for i in $(seq 0 8)
do
    # Inner loop
    for j in $(seq $(($i+1)) 9)
    do
        # Use sed to replace #O1# with i and #O2# with j in c1.txt, output to coptic.c
        sed -e "s/#O1#/$i/g" -e "s/#O2#/$j/g" template.c > coptic.c

        # Execute the perl script
        time ../tool/coptic.pl coptic.c

        # Run the C program 'shuffle' and redirect output to file
        ./shuffle > "out/${i}${j}.txt"
        mv coptic.coptic/default.txt "coptic.coptic/${i}${j}.txt"
    done
done

grep "FINAL SCORE" out/*.txt | awk -F 'FINAL' '{ print "FINAL" $2 " in " $1 }' | sort | tee results.txt | head -n 1