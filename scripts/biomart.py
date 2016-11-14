#!/usr/bin/env python
"""Annotate a list of genes using biomart module.

Usage:

./biomart.py -
./biomart.py genes.txt
cat genes.txt | ./biomart.py
"""
import fileinput
from omics import biomart

if __name__ == "__main__":
    genes = []
    for line in fileinput.input():
        genes.append(line.strip())
    if genes:
        biomart.annotate(genes, verbose=True)
