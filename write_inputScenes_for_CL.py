# given a text list of scenes, spit out string that can be used in manage.py --scenes i.e.:
# 'path/to/scene1.ntf' '/path/to/scene2.ntf'


#import os
#import sys



#tfile = raw_input("Enter the full path to the input text list: ")
tfile = r'C:\\Users\\mwooten3\\Desktop\\del.txt'

with open(tfile, 'r') as pl:
    scenes = pl.read().splitlines()


##print scenes
##print len(scenes)


outStr = ''

for s in scenes:
    outStr += "'{}' ".format(s)

print "{} scene inputs as string for CL:\n".format(len(scenes))
print outStr
