"""Gene Set Analysis Module
"""
from GeneSetCollection import GeneSetCollect

def enrichment(gene_list, gene_set, background, alternative="two-sided", verbose=True):
    """Gene set enrichment analysis by Fisher Exact Test.
    
    gene_list  : query gene list
    gene_set   : predefined gene set
    background : background gene set
    alternative: {'two-sided', 'less', 'greater'}, optional
    verbose    : print results or not
    
    Return: odds ratio (prior), p-value.
    
    See http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html
    To-do: to support a whole genome for default background?
    """
    from scipy.stats import fisher_exact
    from math import log10
    L = set(gene_list) & set(background)
    S = set(gene_set) & set(background)
    a = len(L & S)
    b = len(L) - a
    c = len(S) - a
    d = len(background) - (a + b + c)
    oddsratio, p_value = fisher_exact([[a, b], [c, d]], alternative)
    if verbose:
        print "2x2 contingency table:"
        print "\t%d\t%d" % (a, b)
        print "\t%d\t%d" % (c, d)
        print "odds ratio:\t%f" % oddsratio
        print "%s P-val:\t%g" % (alternative, p_value)
        print "-log(P-val):\t%f" % -log10(p_value)
    return oddsratio, p_value
