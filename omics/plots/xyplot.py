"""xyplot: plot the relationship between x and y (plus z)

Examples:
    
>>> fig = xyplot(df, x='BMI', y='AGE', hue='GENDER')  # numeric vs numeric
>>> ax = xyplot(df, x='COHORT', y='PC1', hue='GENDER')  # categorical vs numeric
>>> ax = xyplot(df, x='COHORT', y='SMCAT', hue='GENDER')  # categorical vs categorical
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

__author__  = "Cho-Yi Chen"
__version__ = "2017.01.24"

def _plot_numeric_vs_numeric(df, x, y, hue=None, **kwargs):
    """Use seaborn's lmplot to plot x vs y with hue (optional).
    """
    if hue:
        df[hue].cat.remove_unused_categories(inplace=True)
    fig = sns.lmplot(x, y, df, hue=hue, **kwargs)
    return fig


def _plot_categorical_vs_numeric(df, x, y, hue=None, **kwargs):
    """Use boxplot plus swarmplot if n_categories < 10, else use stripplot.
    """
    df[x].cat.remove_unused_categories(inplace=True)
    if hue:
        df[hue].cat.remove_unused_categories(inplace=True)
    n_categories = len(df[x].cat.categories)
    if n_categories < 10:
        figsize = (1.2 * n_categories, 4)
        plt.figure(figsize=figsize)
        if df.shape[0] < 1000:
            ax = sns.boxplot(x, y, data=df, color='white', width=0.6)
            ax = sns.swarmplot(x, y, hue=hue, data=df, alpha=.8, size=3, **kwargs)
        else:
            ax = sns.boxplot(x, y, hue=hue, data=df, width=0.6)
        if hue:
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title=hue)
    else:
        ax = sns.stripplot(x, y, hue=hue, data=df, **kwargs)
        labels = plt.gca().get_xticklabels()
        plt.setp(labels, fontsize=6)
    return ax


def _plot_categorical_vs_categorical(df, x, y, hue=None, **kwargs):
    """Use crosstab plus heatmap. (y: rows, x: cols)
    """
    columns = [df[x], df[hue]] if hue else df[x]
    crosstab = pd.crosstab(df[y], columns)
    ax = sns.heatmap(crosstab, annot=True, fmt='d', linewidths=1, **kwargs)
    return ax


def xyplot(df, x, y, hue=None, rotate_xlabels=False, fit_reg=True, **kwargs):
    """Plot the relationship between x and y with optional hue.
    
    df: dataframe
    x, y: column names (numeric or categorical)
    hue: categorical column name (optional)
    rotate_xlabels: to rotate xlabels by 90 degrees
    fit_reg: for lmplot only
    
    Return: axes or figure object.
    
    Examples:
    
    >>> fig = xyplot(df, x='BMI', y='AGE', hue='GENDER')  # numeric vs numeric
    >>> ax = xyplot(df, x='COHORT', y='PC1', hue='GENDER')  # categorical vs numeric
    >>> ax = xyplot(df, x='COHORT', y='SMCAT', hue='GENDER')  # categorical vs categorical
    """
    is_categorical = lambda s: df[s].dtype.name == "category"
    is_numeric     = lambda s: np.issubdtype(df[s].dtype, np.number)

    # plotting according to datatypes
    if is_categorical(x) and is_categorical(y):
        obj = _plot_categorical_vs_categorical(df, x, y, hue, **kwargs)
    elif is_categorical(x) and is_numeric(y):
        obj = _plot_categorical_vs_numeric(df, x, y, hue, **kwargs)
    elif is_numeric(x) and is_categorical(y):
        obj = _plot_categorical_vs_numeric(df, y, x, hue, **kwargs)
    elif is_numeric(x) and is_numeric(y):
        obj = _plot_numeric_vs_numeric(df, x, y, hue, fit_reg=fit_reg, **kwargs)
    else:
        raise "Error: Unsupported datatype for df[x] or df[y]."
    
    # adjusting elements
    if rotate_xlabels:
        labels = plt.gca().get_xticklabels()
        plt.setp(labels, rotation=90)

    return obj
