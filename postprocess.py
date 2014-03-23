#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright © 2011 University of Zürich
# Author: Rico Sennrich <sennrich@cl.uzh.ch>

# Remove features and optionally limit number of tagging ambiguities displayed

from __future__ import unicode_literals, print_function
import sys
import codecs

i_nbest = int(sys.argv[1])
tag_position = 14

if sys.version_info < (3, 0):
    sys.stdin = codecs.getreader('UTF-8')(sys.stdin)
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)


for line in sys.stdin:
    
    linelist = line.split()
    
    if not linelist: #empty lines
        print('')
        continue
 
    #n-best tagging (sentence level)
    if line.startswith('#') and len(linelist) == 3:
        print("{0}{1} {2}".format(linelist[0], linelist[1], linelist[2]))
        continue
   
    #only print word and tag
    if i_nbest == 1:
        print("{0}\t{1}".format(linelist[0], linelist[tag_position]))
        
    #print word and n-best list
    elif i_nbest > 1:
        if line.startswith("#") and len(linelist) < 10:
            continue
        
        alts = [item.split('/') for item in linelist[tag_position+1:]]
        nbest = sorted(alts, key=lambda x: float(x[1]), reverse=True)[:i_nbest]
        nbest_str = '\t'.join(tag+'/'+str(prob) for (tag, prob) in nbest)
        
        print("{0}\t{1}".format(linelist[0], nbest_str))

