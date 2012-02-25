#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: University of Zurich
# Author: Rico Sennrich

# Converts output of morphisto (morphological analyzer) into POS tags in STTS tagset
# Sample call: python morphisto_getpos.py < FILE
# FILE is file that contains the output of morphisto morphological analysis
# output is one token per line, giving all possible POS tags of the words in STTS format

# $ echo -e "> kommen\nkommen<+V><Inf>\nkommen<+V><1><Pl><Pres><Ind>\nkommen<+V><1><Pl><Pres><Konj>\nkommen<+V><3><Pl><Pres><Ind>\nkommen<+V><3><Pl><Pres><Konj>" | python morphisto_getpos.py
# kommen    VVFIN VVINF


import sys
import re

#maps from morphisto tags to stts tags
map_stts = {}
map_stts['DEM'] = 'PD'
map_stts['INDEF'] = 'PI'
map_stts['POSS'] = 'PPOS'
map_stts['REL'] = 'PREL'
map_stts['WPRO'] = 'PW'
map_stts['PPRO'] = 'PPER'
map_stts['PREP/ART'] = 'APPRART'
map_stts['PREP'] = 'APPR'
map_stts['ORD'] = 'ADJA'
map_stts['POSTP'] = 'APPO'
map_stts['CIRCP'] = 'APZR'
map_stts['VPRE'] = 'PTKVZ'
map_stts['PROADV'] = 'PAV'
map_stts['INTJ'] = 'ITJ'
map_stts['SYMBOL'] = 'XY'
map_stts['WADV'] = 'PWAV'
map_stts['CHAR'] = 'XY'


#get stts part_of_speech tag from morphisto output
def get_true_pos(raw_pos,line):
    pos = map_stts.get(raw_pos,raw_pos)
    pos2 = None

    if raw_pos == 'V': 
    
        #stts tagset distinguishes between VV, VA and VM
        if line.startswith('<CAP>'):
            line = line[5:]
        if line.startswith('haben') or line.startswith('werden') or line.startswith('sein'):
            pos += 'A'
        elif line.startswith(u'dürfen') or line.startswith(u'können') or line.startswith('sollen') or line.startswith(u'müssen') or line.startswith(u'mögen') or line.startswith(u'wollen'):
            pos += 'M'     
        else:
            pos += 'V'
        
        #stts tagset distinguishes between VVINF, VVFIN, VVPP and VVIZU
        if '<Inf>' in line:
            if '<zu>' in line:
                pos += 'IZU'
            else:
                pos += 'INF'
        elif '<PPast>' in line:
            pos += 'PP'
        elif '<Ind>' in line or '<Konj>' in line:
            pos += 'FIN'
            
        elif '<Imp>' in line:
            pos += 'IMP'
            
        elif '<PPres>' in line:
            pos = 'ADJD'
            
        else:
            sys.stderr.write('FIN or INF or PP?: '+line.encode("UTF-8")+'\n')
    
    #distinction between ADJA and ADJD
    elif raw_pos == 'ADJ':
        if '<Pred>' in line or '<Adv>' in line:
            pos += 'D'
        else:
            pos += 'A'
    
    #map pronouns to stts tagset
    elif pos in ['PD','PI','PP','PREL','PW','PPOS']:
        
        if '<pro>' in line:
            if pos == 'PI' and '<mD>' in line:
                pos2 = pos + 'DAT'
            else:
                pos2 = pos + 'AT'
            pos += 'S'
        elif '<subst>' in line:
            pos += 'S'
        else:
            if pos == 'PI' and '<mD>' in line:
                pos += 'DAT'
            else:
                pos += 'AT'
           
    elif raw_pos == 'KONJ':
        if '<Vgl>' in line:
            pos = 'KOKOM'
        elif '<Inf>' in line:
            pos = 'KOUI'
        elif '<Sub>' in line:
            pos = 'KOUS'
        elif '<Kon>' in line:
            pos = 'KON'
            
    elif raw_pos == 'PTKL':
        if '<Ant>' in line:
            pos = 'PTKANT'
        elif '<Neg>' in line:
            pos = 'PTKNEG'
        elif '<zu>' in line:
            pos = 'PTKZU'
        elif '<Adj>' in line:
            pos = 'PTKA'
        elif '<Vz>' in line:
            pos = 'PTKVZ'
          
    elif pos == 'PPER':
        if '<refl>' in line:
            pos = 'PRF'
        elif '<prfl>' in line:
            pos = 'PRF'
            pos2 = 'PPER'
            
    return pos,pos2


if __name__ == '__main__':
    
    re_mainclass = re.compile(u'<\+(.*?)>')
    posset = set()
    word = ''
    
    for line in sys.stdin:
        line = line.rstrip().decode('UTF-8')
        
        if line.startswith('>'):
            if word:
                print("{0}\t{1}".format(word.encode('UTF-8'),' '.join(sorted(posset))))
                posset = set()
            word = line[2:]
            continue

        if line.startswith('no result'):
            continue
        
        raw_pos = re_mainclass.search(line).group(1)
        pos,pos2 = get_true_pos(raw_pos,line)

        posset.add(pos)
        if pos2:
            posset.add(pos2)
            
    print("{0}\t{1}".format(word.encode('UTF-8'),' '.join(sorted(posset))))