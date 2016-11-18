#!/usr/bin/env python
"""Gene set enrichment analysis using enrichr API.

Accept input gene list from stdin or text file(s). One gene in a line.
Downloaded enrichment results will be saved to a combined Excel file.

Usage:

./enrichr.py -
./enrichr.py genes.txt [...]
cat genes.txt | ./enrichr.py
"""
import fileinput
from omics import enrichr

if __name__ == "__main__":
    # get input genes
    genes = [line.strip() for line in fileinput.input()]

    if genes:
        genesets = enrichr.genesets['general']
        enrichr.run_enrichr(genes, genesets, verbose=False)
    else:
        print "Error: No input genes."
        print __doc__
