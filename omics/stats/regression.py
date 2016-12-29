"""Regression
"""
import numpy as np
import scipy.stats as sps
import matplotlib.pyplot as plt

__version__ = '16.12.28'
__author__ = 'Cho-Yi Chen'

def basic_regression(x, y):
    """Do 3 basic regression (linear, exponential, and power) like in Excel.
    
    x, y -- two array-like vectors of measurements.
    
    Return {'linear': [slope, intercept, r_value, p_value, std_err],
            'exponential': ...,
            'power': ...}.
    """
    return {'linear': sps.linregress(x, y),
            'exponential': sps.linregress(x, np.log(y)),
            'power': sps.linregress(np.log(x), np.log(y))}

def plot_basic_regression_lines(x, y, ax=None, alpha=[.9, .9, .9]):
    """Plot 3 basic regression lines into a pre-existed figure.

    Linear, exponential, and power (Just like the trendlines in Excel)

    x, y -- array of measurements.

    Tips: to hide any one of the regression lines, just set its alpha to 0.

    No return, just plotting.
    """
    D = basic_regression(x, y)

    if ax is None:
        ax = plt.gca()
    x = np.linspace(*ax.get_xlim())

    # plot linear regression
    if alpha[0]:
        a, b, r, p, e = D['linear']
        y = a * x + b
        text = "$y = %.2fx%+.2f$, $R^2 = %.2f$" % (a, b, r**2)
        ax.plot(x, y, '--', label=text, alpha=alpha[0])

    # plot exponential regression
    if alpha[1]:
        a, b, r, p, e = D['exponential']
        y = np.exp(b) * np.exp(a*x)
        text = "$y = %.2fe^{%.2fx}$, $R^2 = %.2f$" % (np.exp(b), a, r**2)
        ax.plot(x, y, '--', label=text, alpha=alpha[1])

    # plot power regression
    if alpha[2]:
        a, b, r, p, e = D['power']
        y = np.exp(b) * x ** a
        text = "$y = %.2fx^{%.2f}$, $R^2 = %.2f$" % (np.exp(b), a, r**2)
        ax.plot(x, y, '--', label=text, alpha=alpha[2])

