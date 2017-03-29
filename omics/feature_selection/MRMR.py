"""MRMR method.

Implementation of Ding (2005) Minimum redundancyi-maximum relevance (MRMR) feature selection method.

Minimum redundancy feature selection from microarray gene expression data.
Ding C, Peng H
J Bioinform Comput Biol. 2005 Apr; 3(2) 185-205
DOI: 10.1142/S0219720005001004, PMID: 15852500
"""
import pandas as pd
from itertools import product

__author__ = "Cho-Yi Chen"
__version__ = "20170205"

def _redundancy(df, S):
    """W_I from equation (2).
    """
    return 1. * sum([df[i][j] for (i, j) in product(S, repeat=2)]) / len(S) ** 2

def _relevance(df, S, y):
    """V_I from equation (3).
    """
    return 1. * sum([df[y][i] for i in S]) / len(S)

def _MID_score(df, S, y):
    """Equation (4).
    """
    return _relevance(df, S, y) - _redundancy(df, S)

def _MIQ_score(df, S, y):
    """Equation (5).
    """
    return _relevance(df, S, y) / _redundancy(df, S)

def MRMR(df, y, n=10, criterion='MID', to_exclude=[]):
    """Heuristic algorithm described on page 188 (p.4).

    df: MI matrix derived from omics.stats.MI
    y: target variable name
    n: how many features to select
    criterion: scoring criterion, either 'MID' or 'MIQ'
    to_exclude: do not search for these feature names

    Return a dataframe of selected features and their MRMR scores (MID or MIQ) indexed by their selection order (starts from 0).
    """
    # Setup
    F = set(df.index) - set([y]) - set(to_exclude)  # initial feature-to-select set
    S = []  # selected feature list
    n = n if n < len(F) else len(F)  # to select n features
    scores = []  # selected feature scores
    maxlen = sorted([len(i) for i in df.index])[-1]  # max feature name length
    
    # Select first feature
    f = df[y][F].idxmax()  # 1st feature: largest MI(f, y)
    S.append(f)
    scores.append(df[y][f])
    F.remove(f)
    print "Selected feature  1 / %d: %*s (MRMR Score = %.2g)" % (n, maxlen, f, df[y][f])
    
    # Select criterion
    if criterion == "MID":
        get_score = lambda f: _MID_score(df, S + [f], y)
    elif criterion == "MIQ":
        get_score = lambda f: _MIQ_score(df, S + [f], y)
    else:
        raise Exception("Unsupported criterion. Must be either MID or MIQ.")    
    
    # Select next feature
    for i in range(1, n):
        f = sorted(F, key=get_score, reverse=True)[0]  # feature w/ largest MRMR score
        s = get_score(f)
        S.append(f)
        scores.append(s)
        F.remove(f)
        print "Selected feature %2d / %2d: %*s (MRMR Score = %.2g)" % (i+1, n, maxlen, f, s)

    return pd.DataFrame({'Name': S, 'Score': scores})
