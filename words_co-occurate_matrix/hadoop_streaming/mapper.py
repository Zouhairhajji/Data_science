#!/usr/bin/env python3

import sys
import os
import re


file_name = os.environ['mapreduce_map_input_file']
file_name = file_name.split('/')[-1]

lines = []
for line in sys.stdin:

    line = line.replace(",", "")

    splitet_str = re.split('\n| |\'', line)
    
    splitet_str = list(filter(None, splitet_str))
    splitet_str = list(filter(lambda x: False if len(x) < 3 else True, splitet_str))

    lines += splitet_str



for loop1 in lines:
    for loop2 in lines:
        if loop1 == loop2:
            continue
        print(file_name, loop1, loop2)
    