#!/usr/bin/python3
import sys
import numpy as np
import re
import matplotlib.pyplot as plt
def field_by_regex(regex,log_file_name):
    with open(log_file_name) as log_file:
        content =log_file.readlines()
    content = [x.strip() for x in content]
    field=[]
    for line in content:
        m = re.search(regex,line)
        if m:
            #field.append(float(m.groups()[fieldnum]))
            field.append(m.groups())
    return field
