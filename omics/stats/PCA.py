"""Principal Component Analysis (PCA)

Wrappers of scikit-learn PCA functions and more:

1. run_pca

Run PCA/MDS/tSNE on the input dataframe and return the pca result and transformed dataframe.

2. plot_pca

Plot 2D or 3D PCA with samples colored by metadata:

  * plot_2d_pca_plot: create and return a seaborn lmplot object
  * plot_3d_pca_plot: create and return a pyplot figure object

3. plot_explained_variance_ratio

Show the explained variance ratios of PCs in a barplot.

4. pca_on_cov_matrix

Run PCA on a covariance/correlation matrix.
"""
import numpy as np
import pandas as pd

__author__ =  "Cho-Yi (Joey) Chen"
__version__ = "17.01.23"

def run_pca(df, using="pca", pc=3, verbose=True):
    """Run sklearn's PCA on a sample-by-feature dataframe.

    df: a dataframe where rows are samples (observations) and columns are features.
    using: pca/mds/tsne
    pc: how many PCs you need
    verbose: additional informaion output

    Note: sklearn uses the LAPACK implementation of the full SVD.
          This function doesn't rescale the input data by default.

    Return a tuple: (sklearn's PCA object, transformed dataframe).
    """
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE, MDS
    # choose from PCA, MDS or t-SNE
    if using == "pca":
        pca = PCA(n_components=pc)
    elif using == "mds":
        pca = MDS(n_components=pc)
    elif using == "tsne":
        pca = TSNE(n_components=pc, init="pca")
    else:
        raise e, "Method %s not supported!" % using
    # run pca
    mat = pca.fit_transform(df.values)
    out = pd.DataFrame(mat, index=df.index, columns=['PC%d' % i for i in range(1, pc+1)])
    # print meta info
    if verbose:
        print "Data dimensions (samples-by-features):", df.shape
        if using == "pca":
            print "Variance explained by top %d PCs:" % pc
            print ', '.join(["%.3g" % i for i in pca.explained_variance_ratio_])
    return pca, out

def plot_2d_pca(pca, data, pData=None, hue=None, title=None, **kwargs):
    """Plot 2D PCA.

    pca: sklearn's PCA object derived from run_pca (at least 2 PCs)
    data: transformed dataframe after pca (column names are 'PC1', 'PC2', ...)
    pData: phenotype dataframe for samples (optional).
    hue: variable name in pData for sample annotation (optional).
    title: title of the figure (optional).
    kwargs: arguments to pass to seaborn.lmplot, e.g., size, palette, ..., etc.

    Return a seaborn's lmplot object.
    """
    import seaborn as sns
    if pData is not None and hue:
        data[hue] = pData[hue]
    g = sns.lmplot('PC1', 'PC2', data, hue=hue, fit_reg=False, **kwargs)
    g.ax.set_xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
    g.ax.set_ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[1] * 100))
    if title:
        g.ax.set_title(title)
    return g

def plot_3d_pca(pca, data, pData=None, hue=None, title=None, figure=None, marker='o', alpha=0.8, ms=4, **kwargs):
    """Plot 3D PCA.

    pca: sklearn's PCA object derived from run_pca.
    data: transformed dataframe after pca.
    pData: phenotype data for samples (optional).
    hue: variable name in pData for sample annotation (optional).
    title: title of the figure (optional).
    figure: figure object to plot on (optional).
    kwargs: arguments to pass to matplotlib.axes.Axes.scatter, e.g., marker, cmap, alpha, ms.

    Return a tuple: (figure object, axes object).
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    fig = figure if figure else plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Update kwargs for plot
    kwargs['marker'] = marker
    kwargs['alpha'] = alpha
    kwargs['ms'] = ms

    # 3D data
    x, y, z = data.iloc[:,0], data.iloc[:,1], data.iloc[:,2]

    # color mapping when hue variable is assigned
    if pData is not None and hue:
        assert all(data.index == pData.index)  # make sure samples are aligned
        hues = pData[hue]  # hue column
        if hue in pData.select_dtypes(include=[np.number]):
            # hue variable is numeric FIXME!
            plt.plot(x, y, z, c=hues, label=hue, **kwargs)
        else:
            # treat hue variable as categorical
            for label in hues.unique():
                trues = (hues == label)
                plt.plot(x[trues], y[trues], z[trues], 'o', label=label, **kwargs)
        plt.legend(loc=0, fontsize='small')
    else:
        # no color mapping
        plt.plot(x, y, z, 'o', **kwargs)

    ax.set_xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
    ax.set_ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[1] * 100))
    ax.set_zlabel('PC3 (%.1f%% var)' % (pca.explained_variance_ratio_[2] * 100))

    if title:
        ax.set_title(title)

    fig.tight_layout()
    return fig, ax

def plot_pca(pca, data, pc=2, **kwargs):
    """Plot 2D/3D PCA.

    pca: PCA object derived from run_pca
    data: transformed data after pca
    pc: 2D or 3D PCA plot
    kwargs: pass to plot_2d_pca or plot_3d_pca

    Return: seaborn's lmplot object (if 2D) or a (fig, ax) tuple (if 3D).
    """
    if pc == 2:
        return plot_2d_pca(pca, data, **kwargs)
    elif pc == 3:
        return plot_3d_pca(pca ,data, **kwargs)
    else:
        raise e, "PC > 3 is not supported!"

def plot_explained_variance_ratio(y, figsize=(4,3), **kwargs):
    """Compare the explained variance ratios of PCs in a barplot.

    y: explained variance ratio, e.g., pca.explained_variance_ratio_
    figsize: pass to pyplot.figure()
    kwargs: pass to seaborn.barplot()

    Recommended style: 'white'.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig = plt.figure(figsize=figsize)
    ax = sns.barplot(range(1, len(y)+1), y, **kwargs)
    ax.set_xlabel('PC')
    ax.set_ylabel('Explained variance ratio')
    sns.despine()

def plot_explained_variance_ratio2(y, figsize=(4,3)):
    """Compare the explained variance ratios of PCs in a barplot.

    y: explained variance ratio, e.g., pca.explained_variance_ratio_
    figsize: pass to pyplot.figure()

    Recommended style: 'white'.
    """
    import matplotlib.pyplot as plt
    cum_var_exp = np.cumsum(y)
    n = len(y)
    plt.figure(figsize)
    plt.bar(range(1, n+1), var_exp[:n], alpha=0.5, align='center', label='individual explained variance')
    plt.step(range(1, n+1), cum_var_exp[:n], where='mid', label='cumulative explained variance')
    plt.ylabel('Explained variance ratio')
    plt.xlabel('Principal components')
    plt.xlim(0, n+1)
    plt.legend(loc='best')
    plt.tight_layout()

def pca_on_cov_matrix(mat):
    """PCA on covariance/correlation matrix.

    mat: can be covariance matrix, standardized covariance matrix, or correlation matrix.
    
    The correlation matrix can be understood as the normalized covariance matrix.

    Return: sorted (eigenvalue, eigenvector) list, explained variance ratio list, projection matrix W.

    Note: Projection Onto the New Feature Space can be yieled by Y = X.dot(W), 
          where X is the raw samples x features matrix.

    Adapted from: http://sebastianraschka.com/Articles/2015_pca_in_3_steps.html
    """
    eig_vals, eig_vecs = np.linalg.eig(mat)
    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs.sort(key=lambda x: x[0], reverse=True)
    # Explained Variance
    var_exp = [(i / sum(eig_vals)) * 100 for i in sorted(eig_vals, reverse=True)]
    # Projection Matrix
    n = mat.shape[0]
    W = np.hstack([eig_vec.reshape(n, 1) for (eig_val, eig_vec) in eig_pairs])
    return eig_pairs, var_exp, W
