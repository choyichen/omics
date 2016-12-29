"""Transcriptomic SNR (tSNR)
"""
import numpy as np

__version__ = '16.12.28'
__author__ = 'Cho-Yi Chen'

def tsnr(X, Y):
    """Transcriptomic SNR (tSNR)

    X: case expression matrix (genes-by-samples)
    Y: ctrl expression matrix (genes-by-samples)

    Return the tSNR (float) between X and Y.
    """
    # See http://docs.scipy.org/doc/scipy/reference/spatial.distance.html for more distance metrics
    from scipy.spatial.distance import euclidean
    m = X.shape[1]
    n = Y.shape[1]
    xmean = X.mean(axis=1)
    ymean = Y.mean(axis=1)
    signal = euclidean(xmean, ymean)
    xvar = np.sum(np.square(np.apply_along_axis(euclidean, 0, X, xmean))) / (m - 1)
    yvar = np.sum(np.square(np.apply_along_axis(euclidean, 0, Y, ymean))) / (n - 1)
    noise = np.sqrt((xvar / m) + (yvar / n))
    return 1. * signal / noise

def tsnr_pval(X, Y, permute=1000):
    """Estimate the P value via permutation test.
    """
    m = X.shape[1]
    n = Y.shape[1]
    snr = tsnr(X, Y)
    Z = np.concatenate([X,Y], axis=1).T
    pool = []
    for _ in xrange(permute):
        np.random.shuffle(Z)
        x = Z[:m,:].T
        y = Z[m:,:].T
        pool.append(tsnr(x, y))
    pool = np.array(pool)
    pval = 1. * sum(pool >= snr) / permute
    return pval if pval != 0 else (0.5 / permute)

def tsnr_boot(X, Y, N=30, boot=1000):
    """Estimate the tSNR via bootstrapping (resampling with replacement)
    
    Warning: It truns out using bootstrapping to estimate the tSNR is not
    a good idea. The estimated tSNR tends to be larger, and is dependent 
    on N (how many samples to pick). It N is close to the sample sizes, 
    it will be more likely to choose repeated data points, thus lowring 
    the randomness of sample distribution and strengthening the signal
    between cases and controls. I think this is biased and should not be
    used.    
    """
    m = X.shape[1]
    n = Y.shape[1]
    out = []
    for i in xrange(boot):
        x = X[:, np.random.choice(m, N, replace=True)]
        y = Y[:, np.random.choice(n, N, replace=True)]
        out.append(tsnr(x, y))
    return np.mean(out), np.median(out), np.std(out)

if __name__ == "__main__":
    print "tSNR between two random matrices:"
    X = np.random.rand(40, 40)
    Y = np.random.rand(40, 40)
    print "tSNR:", tsnr(X, Y)
    print "Pval:", tsnr_pval(X, Y)

    print "tSNR between two identical matrices:"
    print "tSNR:", tsnr(X, X + 1)
    print "Pval:", tsnr_pval(X, X + 1)
