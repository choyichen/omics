#!/usr/bin/env python
"""Annotate a list of genes using biomart module.

Accept input gene list from stdin or text file(s).
One gene in a line.

Usage:

./biomart.py -
./biomart.py genes.txt [...]
cat genes.txt | ./biomart.py
"""
import fileinput
from omics import biomart

if __name__ == "__main__":
    # get input genes
    genes = [line.strip() for line in fileinput.input()]

    if genes:
        biomart.annotate(genes, verbose=True)
    else:
        print "Error: No input genes."
        print __doc__
