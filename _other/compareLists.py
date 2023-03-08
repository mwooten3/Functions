# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 15:00:03 2020
@author: mwooten3

Find the differences between two lists
"""

import os
"""
import sys
"""

print "NOTE: Returning a maximum of 2 lists: 'list1-list2' and 'list2-list1'"

# User input variables
listF1 = 'E:\MaggieData\AIST\TTE\compareLists\list1.txt'
listF2 = 'E:\MaggieData\AIST\TTE\compareLists\list2.txt'
outdir = 'E:\MaggieData\AIST\TTE\compareLists'

bname1 = os.path.basename(listF1).replace('.txt', '')
bname2 = os.path.basename(listF2).replace('.txt', '')

#import pdb; pdb.set_trace()
with open(listF1, 'r') as l1:
    list1 = [i.strip() for i in l1.readlines()]

with open(listF2, 'r') as l2:
    list2 = [i.strip() for i in l2.readlines()]

# list1-list2
# Items in list1 but not list2
out1 = os.path.join(outdir, '{}-{}_difference.txt'.format(bname1, bname2))
for i in list1:
    if i in list2:
        continue
    with open(out1, 'a') as o1:
        o1.write('{}\n'.format(i))


# list2-list1
# Items in list2 but not list1
out2 = os.path.join(outdir, '{}-{}_difference.txt'.format(bname2, bname1))
for j in list2:
    if j in list1:
        continue
    with open(out2, 'a') as o2:
        o2.write('{}\n'.format(j))



