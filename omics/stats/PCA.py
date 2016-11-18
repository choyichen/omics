"""Principal Component Analysis (PCA)

Wrappers of scikit-learn PCA functions and more:

1. run_pca

Run PCA/MDS/tSNE on the input dataframe and return the pca result and transformed dataframe.

2. plot_pca

Plot 2D or 3D PCA with samples colored by metadata:

  * plot_2d_pca_plot: create and return a seaborn lmplot object
  * plot_3d_pca_plot: create and return a pyplot figure object
"""
from pylab import *
import pandas as pd

__author__ =  "Cho-Yi (Joey) Chen"
__version__ = "16.11.16"

def run_pca(df, using="pca", pc=3):
    """Run PCA on a sample-by-feature dataframe.

    df: a dataframe where rows are samples (observations) and columns are features.

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
    return pca, out

def plot_2d_pca(pca, data, pData=None, hue=None, title=None, **kwargs):
    """Plot 2D PCA.

    pca: PCA object derived from run_pca.
    data: transformed dataframe after pca.
    pData: phenotype data for samples (optional).
    hue: variable name in pData for sample annotation (optional).
    title: title of the figure (optional).
    kwargs: arguments to pass to seaborn.lmplot, e.g., size, palette, ..., etc.

    Return a seaborn's lmplot object.
    """
    import seaborn as sns
    if pData is not None and hue is not None:
        out[hue] = pData[hue]

    g = sns.lmplot('PC1', 'PC2', out, hue=hue, fit_reg=False, **kwargs)
    g.ax.set_xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
    g.ax.set_ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[1] * 100))

    if title:
        g.ax.set_title(title)
    return g

def plot_3d_pca(pca, data, pData=None, hue=None, title=None, figure=None, **kwargs):
    """Plot 3D PCA.

    pca: PCA object derived from run_pca.
    data: transformed dataframe after pca.
    pData: phenotype data for samples (optional).
    hue: variable name in pData for sample annotation (optional).
    title: title of the figure (optional).
    figure: figure object to plot on (optional).
    kwargs: arguments to pass to matplotlib.axes.Axes.scatter, e.g., s, c, marker, cmap, alpha.

    Return a tuple: (figure object, axes object).
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure() if figure is None else figure
    ax = fig.add_subplot(111, projection='3d')

    # 3D data
    x, y, z = data.iloc[:0], data.iloc[:1], data.iloc[:2]

    # color mapping when hue variable is assigned
    if pData is not None and hue is not None:
        c = pData[hue]
        if np.issubdtype(c.dtype, np.number):
            # hue variable is numeric
            ax.scatter(x, y, z, c=c, label=hue, **kwargs)
        else:
            # hue variable should be categorical
            labels = list(set(c))
            colors = np.linspace(0, 1, len(labels))
            for i, label in enumerate(labels):
                trues = (c == label)
                ax.scatter(x[trues], y[trues], z[trues], colors[i], label=label, **kwargs)
        plt.legend(loc=0)
    else:
        # no color mapping
        ax.scatter(x, y, z, **kwargs)

    ax.set_xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
    ax.set_ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[1] * 100))
    ax.set_ylabel('PC3 (%.1f%% var)' % (pca.explained_variance_ratio_[2] * 100))

    if title:
        ax.set_title(title)
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
        raise e, "PC can only be 2 or 3!"

# legacy code
#def mypca(expr, classes, labels, colors=None, figname=None, figtitle=None, alpha=1., dpi=100, \
          #figsize=None, legend_loc='best', pc=2, using="pca", annot=None, verbose=True):
    #"""PCA on expression profile. (old)

    #expr - expression matrix (genes-by-samples) (2-dimensional float-only numpy.ndarray)
    #classes - a list of sample classes, each class contains a list of sample indexes, e.g., [[1,2,3], [4,5,6]]
    #labels - a list of class labels, must be in same length as classes, e.g., ['Female', 'Male']
    #colors - specify a label-to-color dict for PCA plot, e.g., dict(zip(labels, sns.color_palette()[:2]))
    #figname - save PCA plot to a file
    #figtitle - a string for figure title
    #alpha - markers' alpha level (transparency)
    #dpi - dpi of PCA plot
    #pc - how many PC to keep, plotting only supports 2D or 3D
    #using - choose from pca or tSNE algorithms
    #annot - a dict contains sample indexes and names for annotatation, e.g., {0: "John", 2: "Mary"}
    #verbose - print meta info

    #Note: PCA will be performed based on whole expression matrix (expr) regardless of the given classes.
          #Class information is only used to color the data points.

    #Return a fitted pca model object.
    #"""
    #from sklearn.decomposition import PCA
    #from sklearn.manifold import TSNE, MDS
    #from mpl_toolkits.mplot3d import Axes3D

    # assertions
    #assert len(classes) == len(labels), "Classes and labels must be in equal lengths!"

    # choose from PCA or t-SNE
    #if using == "pca":
        #pca = PCA(n_components=pc)
    #elif using == "tsne":
        #pca = TSNE(n_components=pc, init="pca")
    #elif using == "mds":
        #pca = MDS(n_components=pc)
    #else:
        #raise e, "Method not supported!"

    # do the model fit
    #X = expr
    #X_new = pca.fit_transform(X.T)  # PCA on X.T and then get transformed X_new

    # print meta info
    #if verbose:
        #print "Title: %s -> %s" % (figtitle, figname)
        #print "Data dimensions (genes-by-samples):", X.shape
        #print len(classes), "classes:", zip(labels, [len(cls) for cls in classes])
        #if using == "pca":
            #print "Variance explained by top %d PCs:" % pc, pca.explained_variance_ratio_

    # plotting
    #if pc == 2:
        #figure(figsize=figsize)
        #for (cls, label) in zip(classes, labels):
            #if colors:
                #plot(X_new[cls, 0], X_new[cls, 1], 'o', label=label, color=colors[label], alpha=alpha)
            #else:
                #plot(X_new[cls, 0], X_new[cls, 1], 'o', label=label, alpha=alpha)
        #xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
        #ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[1] * 100))
        #legend(loc=legend_loc)
    #elif pc == 3:
        #figure(figsize=figsize)
        #ax = gca(projection='3d')
        #for (cls, label) in zip(classes, labels):
            #if colors:
                #ax.plot(X_new[cls, 0], X_new[cls, 1], X_new[cls, 2], 'o', label=label, color=colors[label], alpha=alpha)
            #else:
                #ax.plot(X_new[cls, 0], X_new[cls, 1], X_new[cls, 2], 'o', label=label, alpha=alpha)
        #ax.set_xlabel('PC1 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
        #ax.set_ylabel('PC2 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
        #ax.set_zlabel('PC3 (%.1f%% var)' % (pca.explained_variance_ratio_[0] * 100))
        #legend(loc=legend_loc)
    #else:
        #print "PC > 3 cannot be drawn."

    #if annot and isinstance(annot, dict):
        #for idx,name in annot.iteritems():
            #annotate(s=name, xy=(X_new[idx, 0], X_new[idx, 1]))
    #if figtitle:
        #title(figtitle)
    #if figname:
        #savefig(figname, dpi=dpi)
    #return pca
