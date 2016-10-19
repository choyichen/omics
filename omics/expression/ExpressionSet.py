"""Definition of ExpressionSet class.

ExpressionSet class mimics R's Bioconductor ExpressionSet.

Note:
  * See omics.io.ExpressionSetIO for associated I/O functions.

Reference:
  * https://www.bioconductor.org/packages/release/bioc/vignettes/Biobase/inst/doc/ExpressionSetIntroduction.pdf

Todo:
  * Add tests.
"""
import pandas as pd

__author__ = "Cho-Yi Chen"
__version__ = "2016.10.16"

class ExpressionSet(object):
    """ExpressionSet class mimics R's Bioconductor ExpressionSet.

    Usage
    -----

    Create an ExpressionSet instance:

      eSet = ExpressionSet(exprs, fData=None, pData=None, **kwargs)

      exprs: expression dataframe (genes x samples)
      fData: feature dataframe (genes x features)
      pData: phenotype dataframe (samples x phenotypes)
      kwargs: metadata (e.g., title) (saved in eSet.meta)

    Test if a given sample/gene exists in the eSet:

    >>> 'ENSG00000000003' in eSet
    True
    >>> 'GTEX.ZXG5.0011.R7b.SM.57WCC' in eSet
    True

    Get/set the metadata:

    >>> eSet.meta['title'] = "Title of the eSet"
    >>> print eSet.meta['title']
    Title of the eSet
    """
    def __init__(self, exprs, fData=None, pData=None, **kwargs):
        self.exprs = exprs  # property
        self.fData = fData  # property
        self.pData = pData  # property
        self.meta = pd.Series(kwargs)  # metadata

    def __str__(self):
        s1 = ('{}\n'
              'exprs: {} features, {} samples\n'
              'fData: {} features, {} attributes\n'
              'pData: {} samples, {} variables\n'
              'features: {}, ..., {}\n'
              'samples: {}, ..., {}\n').format(
              self.meta.get('title', 'ExpressionSet instance'),
              self._exprs.shape[0], self._exprs.shape[1],
              self._fData.shape[0], self._fData.shape[1],
              self._pData.shape[0], self._pData.shape[1],
              self._exprs.index[0], self._exprs.index[-1],
              self._exprs.columns[0], self._exprs.columns[-1])
        s2 = '\n'.join(["{}: {}".format(k, v) for k,v in self.meta.iteritems() if k != 'title'])
        return s1 + s2

    def __repr__(self):
        return self.__str__()

    def __contains__(self, item):
        return item in self._exprs or item in self._exprs.index

    def subset(self, features=slice(None), samples=slice(None)):
        """Subset by given features/samples.

        features: a sequence of feature names (default: all features)
        samples: a sequence of sample names (default: all samples)

        Return a new ExpressionSet.
        """
        exprs = self._exprs.loc[features, samples]
        fData = self._fData.loc[features] if not self._fData.empty else pd.DataFrame()
        pData = self._pData.loc[samples]  if not self._pData.empty else pd.DataFrame()
        return ExpressionSet(exprs, fData, pData, **self.meta)

    @property
    def exprs(self):
        """Expression dataframe (genes x samples)"""
        return self._exprs

    @exprs.setter
    def exprs(self, df):
        assert isinstance(df, pd.DataFrame)
        self._exprs = df

    @property
    def fData(self):
        """Feature dataframe (genes x feature attributes)"""
        return self._fData

    @fData.setter
    def fData(self, df):
        assert df is None or all(df.index == self._exprs.index)  # check if features are aligned
        self._fData = df if df is not None else pd.DataFrame()  # if df is None, use an empty DataFrame

    @property
    def pData(self):
        """Phenotype dataframe (sample x phenotype variables)"""
        return self._pData

    @pData.setter
    def pData(self, df):
        assert df is None or all(df.index == self._exprs.columns)  # check if samples are aligned
        self._pData = df if df is not None else pd.DataFrame()  # if df is None, use an empty DataFrame
