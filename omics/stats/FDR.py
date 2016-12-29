"""Multiple test correction.
"""
__version__ = '16.12.28'
__author__ = 'Cho-Yi Chen'

def Bonferroni(P, alpha=0.05):
    """Return the Bonferroni threshold for a vector of P-values."""
    return alpha / len(P)

def FDR_BH_threshold(P, alpha=0.05):
    """Return the significant p-value threshold using Benjamini and Hochberg's method.
    
    P -- A sequence of P-values
    alpha -- Significance level
    """
    Pr = sorted(P, reverse=True)
    m = len(Pr)
    for i in xrange(m):
        threshold = alpha * (m-i) / m
        if Pr[i] <= threshold:
            return threshold
    return threshold

def FDR_BL_threshold(P, alpha=0.05):
    """Return the significant p-value threshold using Benjamini and Liu's method.
    
    P -- A sequence of P-values
    alpha -- Significance level
    """
    Pr = sorted(P)
    m = len(Pr)
    for i in xrange(m):
        threshold = alpha * m / ((m-i) ** 2)
        if Pr[i] >= threshold:
            return threshold
    return threshold
