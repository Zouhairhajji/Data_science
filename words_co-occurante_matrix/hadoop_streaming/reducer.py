#!/usr/bin/env python3

import sys


dictionnary = {}

for line in sys.stdin:
    line = line.strip().split(' ')
    
    context = line[0]
    word1 = line[1]
    word2 = line[2]

    dict_key1 = (context, word1, word2 )
    dict_key2 = (context, word2, word1 )


    if ( (dict_key1 in dictionnary) &  (dict_key2 in dictionnary) ):
        dictionnary[dict_key1] += 1
        dictionnary[dict_key2] += 1
    else :
        dictionnary[dict_key1] = 1
        dictionnary[dict_key2] = 1



for tuple in dictionnary:
    context = tuple[0]
    words =  (tuple[1], tuple[2])
    occur = int(dictionnary[tuple]/2 -1)

    print(context, words, occur)