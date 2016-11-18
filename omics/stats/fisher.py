"""Fisher's Exact test.

Wrapper of scipy.stats.fisher_exact.
"""

__version__ = '16.11.16'
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

    Examples:

    >>> odds, pval = fisher_exact_test(8, 10, 9, 16)
    Odds ratio: 20.00
    P-value: 3.50e-02

    >>> odds, pval = fisher_exact_test(5, 5, 6, 10)
    Odds ratio: inf
    P-value: 4.76e-02

    >>> odds, pval = fisher_exact_test(43, 45, 60, 69)
    Odds ratio: 8.85
    P-value: 6.65e-03

    >>> u = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    >>> U = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
    >>> v = set([1, 2, 3, 4, 5, 6, 7, 8, 11])
    >>> V = set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
    >>> odds, pval = fisher_exact_test(u, v, U, V)
    Odds ratio: 20.00
    P-value: 3.50e-02

    References:

    * http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.stats.fisher_exact.html
    * http://mathworld.wolfram.com/FishersExactTest.html
    * http://udel.edu/~mcdonald/statfishers.html
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
