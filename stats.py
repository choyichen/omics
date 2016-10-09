"""Modules for statistics functions
"""

__version__ = '0.1.161009'
__author__ = 'Cho-Yi Chen'

def fisher_2d(a, b, c, d, verbose=True):
    """Fisher's exact test by giving a 2-dim contigency table:

    a     (b-a)    b
    (c-a) (d-b-c+a)
    c              d

    Return a/b, odds ratio, p-value
    """
    pct = 1. * a / b
    oddsratio, pvalue = fisher_exact([[a, b-a], [c-a, d-b-c+a]])
    if verbose:
        print "%d/%d = %d%%" % (a, b, pct * 100)
        print "Odds ratio: %.2f" % oddsratio
        print "P-value: %.2e" % pvalue
    return pct, oddsratio, pvalue

def fisher_enrichment(u, v, U, V, verbose=True):
    """Fisher's exact test by giving two sets.

    u, U: gene set u and its universe U
    v, V: gene set v and its universe V

    Return percentage, odds ratio, p-value
    """
    background = U & V  # consensus background
    nu = u & background  # new u
    nv = v & background  # new v
    a = len(nu & nv)
    b = len(nu)
    c = len(nv)
    d = len(background)
    return fisher_2d(a, b, c, d, verbose)

