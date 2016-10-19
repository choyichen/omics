"""Fisher's Exact test.

Wrapper functions of scipy.stats.fisher_exact.

TODO:
  * Add doctests
"""

__version__ = '0.1.161015'
__author__ = 'Cho-Yi Chen'

def _test_by_marginal_numbers(a, b, c, d):
    """Fisher's exact test by giving marginal numbers from a 2-dim contigency table:

    a     (b-a)    b
    (c-a) (d-b-c+a)
    c              d

    Return odds ratio, p-value.
    """
    from scipy.stats import fisher_exact
    oddsratio, pvalue = fisher_exact([[a, b-a], [c-a, d-b-c+a]])
    return oddsratio, pvalue

def _test_by_set_sizes(u, v, U, V):
    """Fisher's exact test by giving two sets.

    u, U: gene set u and its universe U
    v, V: gene set v and its universe V

    Return odds ratio, p-value.
    """
    background = U & V  # consensus background
    nu = u & background  # new u
    nv = v & background  # new v
    a = len(nu & nv)
    b = len(nu)
    c = len(nv)
    d = len(background)
    return _test_by_marginal_numbers(a, b, c, d)

def fisher_exact_test(a, b, c, d, verbose=True):
    """Fisher's exact test by giving marginal numbers or sets.

    If a, b, c, d, were numbers, they should represent marginal numbers in a contigency table.

    a     (b-a)    b
    (c-a) (d-b-c+a)
    c              d

    If a, b, c, d, were sets, they should represent two gene sets and their background sets.

    a, b: gene set a and its universe b
    c, d: gene set c and its universe d

    Return odds ratio, p-value.
    """
    if all([isinstance(i, int) for i in (a,b,c,d)]):
        # call by giving four marginal numbers in a contigency table
        oddsratio, pvalue =  _test_by_marginal_numbers(a,b,c,d)
    if all([isinstance(i, set) for i in (a,b,c,d)]):
        # call by giving two gene sets and their background sets
        oddsratio, pvalue =  _test_by_set_sizes(a,b,c,d)
    if verbose:
        print "Odds ratio: %.2f" % oddsratio
        print "P-value: %.2e" % pvalue
    return oddsratio, pvalue

