#!usr/bin/env python
# -*- coding: utf-8 -*-
"""
clean line numbers out of .po files to get rid of annoying merge issues
"""
import os


patterns = ['#:']


def clean_po(messages_dir):
    buf = []
    po = os.path.join(messages_dir, 'messages.po')
    print 'cleaning line comments out of {}..'.format(po)
    with open(po) as f:
        for line in f:
            include = True
            for pattern in patterns:
                if line.startswith(pattern):
                    include = False
                    break
            if include:
                buf.append(line)
    with open(po, 'w') as f:
        f.write(''.join(buf))
        print 'done'

root = os.path.dirname(__file__)

for p in os.listdir(root):
    d = os.path.join(root, p, 'LC_MESSAGES')
    if os.path.isdir(d):
        print 'found language', p
        clean_po(d)
