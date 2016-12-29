"""Module for mutual information.

This module defines the following functions, based on scikit-learn:

* MI(x, y): Get MI between two vectors. Choose the method automatically based on variable types of x and y.
* normalized_MI_matrix(df): Get a pair-wise normalized MI matrix from a feature dataframe.

NOTE: Some functions have not yet fully implemented: MI(x, y).
"""
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif

def MI(x, y, random_state=None):
    """Get mutual information (MI)  between two pandas series.

    x,y: any numeric or categorical vectors.

    Return the mutual information between x and y.
    """
    # pandas's category encodes nan as -1 using integer coding
    is_categorical = lambda x: x.dtype.name == 'category'
    if is_categorical(x) and is_categorical(y):
        return mutual_info_classif(x.cat.codes.values.reshape(-1, 1), y.cat.codes, discrete_features=True, random_state=random_state)[0]
    elif is_categorical(x) and not is_categorical(y):
        return mutual_info_regression(x.cat.codes.values.reshape(-1, 1), y, discrete_features=True, random_state=random_state)[0]
    elif not is_categorical(x) and is_categorical(y):
        return mutual_info_classif(x.values.reshape(-1, 1), y.cat.codes, discrete_features=False, random_state=random_state)[0]
    else:
        # both x and y are numeric
        return mutual_info_regression(x.values.reshape(-1, 1), y, discrete_features=False, random_state=random_state)[0]

def normalized_MI_matrix(df, seed=None, verbose=False):
    """Compute a normalized mutual information matrix from a dataframe.

    df: An n samples x k features dataframe.
    seed: Seed for random number generator.
    verbose: To print out log message or not.

    Return two k x k dataframe matrixes: (MI, normalized MI).

    Ref https://en.wikipedia.org/wiki/Mutual_information#Normalized_variants
    """
    df = df.copy()  # make a copy
    nrow, ncol = df.shape  # row: samples, col: variables
    if verbose: print "Input dataframe: %d samples x %d features" % (nrow, ncol)

    # get a boolean mask for categorical varialbes
    is_categorical = df.columns.isin(df.select_dtypes(['category']).columns)
    if verbose: print "%d features are categorical" % sum(is_categorical)

    # do integer encoding for categorical variables
    for i,x in df.select_dtypes(['category']).iteritems():
        df[i] = x.cat.codes.astype('float64')

    # calculate pair-wise MI
    if verbose: print "Computing pair-wise MI ..."
    out = []
    for i in xrange(ncol):
        #if verbose: print df.columns[i],
        X = df.iloc[:, i:]  # feature matrix
        y = df.iloc[:, i]   # target variable
        if is_categorical[i]:
            out.append(mutual_info_classif(X, y, discrete_features=is_categorical[i:], random_state=seed))
        else:
            out.append(mutual_info_regression(X, y, discrete_features=is_categorical[i:], random_state=seed))
    MIs = np.concatenate(out) 

    # fill in a square MI matrix
    mat = np.zeros((ncol, ncol))
    mat[np.triu_indices(ncol)] = MIs # fill in upper triangle
    mat.T[np.triu_indices(ncol)] = MIs  # fill in upper triangle

    # normalized an MI matrix
    if verbose: print "Normalize MI ..."
    mat2 = np.zeros((ncol, ncol))
    for i,j in np.dstack(np.triu_indices(ncol))[0]:
        mat2[i, j] = mat2[j, i] = mat[i, j] / np.sqrt(mat[i, i] * mat[j, j])  # normalized MI

    return (pd.DataFrame(mat, index=df.columns, columns=df.columns), \
            pd.DataFrame(mat2, index=df.columns, columns=df.columns))
