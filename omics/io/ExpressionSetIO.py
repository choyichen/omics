"""I/O functions that operate on omics ExpressionSet objects.

Supported:
  * I/O from/to Bioconductor ExpressionSet (RData)
  * I/O from/to HDF5 storage (Pandas dataframes)

Input:
  * RData2ExpressionSet(RData, assay='exprs', fFactors='auto', pFactors='auto')
  * HDF52ExpressionSet(HDF5, assay='exprs', fData='fData', pData='pData')

Output:
  * ExpressionSet2RData(eSet, RData)
  * ExpressionSet2HDF5(eSet, HDF5)

References:
  * http://pandas.pydata.org/pandas-docs/stable/r_interface.html
  * https://www.bioconductor.org/packages/release/bioc/vignettes/Biobase/inst/doc/ExpressionSetIntroduction.pdf

Todo:
  * Add tests.
"""
import readline

import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

from omics.expression.ExpressionSet import ExpressionSet

__author__ = "Cho-Yi Chen"
__version__ = "2016.10.16"

# ================================================================================
# Auxiliary functions
# ================================================================================

def _read_ExpressionSet_RData(RData):
    """Read ExpressionSet RData to Rpy2 robjects.

    RData: Path to the input RData file.
           ExpressionSet must be the only object in the RData.

    Return Rpy2's eSet object, assayData, featureData, phenotypeData.
    """
    importr('Biobase')
    rdata = r.load(RData)
    eSet = r.get(rdata)           # rpy2 ExpressionSet object (assumed)
    assayData = r.assayData(eSet) # rpy2 environment object
    fData = r.fData(eSet)         # rpy2 DataFrame object
    pData = r.pData(eSet)         # rpy2 DataFrame object
    return eSet, assayData, fData, pData

def _parse_assayData(assayData, assay):
    """Parse Rpy2 assayData (Environment object)

    assayData: Rpy2 Environment object.
    assay: An assay name indicating the data to be loaded.

    Return a parsed expression dataframe (Pandas).
    """
    pandas2ri.activate()
    mat = assayData[assay]  # rpy2 expression matrix object
    data = pandas2ri.ri2py(mat)
    features = pandas2ri.ri2py(r.rownames(mat))
    samples = pandas2ri.ri2py(r.colnames(mat))
    return pd.DataFrame(data, index=features, columns=samples)

def _parse_rdataframe(rdf, factor_cols='auto'):
    """Parse an Rpy2 DataFrame.

    rdf: An Rpy2 DataFrame object.
    factor_cols: A list of column names indicating categorical data.
      If 'auto', categorical columns will be determined by their contents, individually.
      If None, do nothing and use the default dtypes.

    Return a pandas dataframe.
    """
    pandas2ri.activate()
    df = pandas2ri.ri2py(rdf)
    if factor_cols == 'auto':
        # Infer if there are categorical data
        n = df.shape[0]
        subdf = df.select_dtypes(include=['integer', 'object'])
        factor_cols = [k for k,v in subdf.iteritems() if n > 10 * len(set(v))]
    if factor_cols:
        # Make each column categorical
        assert not isinstance(factor_cols, str)
        for k in factor_cols:
            df[k] = df[k].astype('category')
    return df

# ================================================================================
# Input functions
# ================================================================================

def RData2ExpressionSet(RData, assay='exprs', fFactors='auto', pFactors='auto', verbose=True, **kwargs):
    """Read R's ExpressionSet (RData) to omics ExpressionSet (eSet)

    RData: Path to the input RData file with only one eSet object inside.
    assay: Assay name to be loaded.
    f/pFactors: List of column names indicating categorical data (factors in R).
      If 'auto', factor columns will be determined by their contents, individually.
      If None, do nothing and use the default dtypes.
    kwargs: Keyword arguments passed to ExpressionSet constructor

    Return a omics ExpressionSet object (eSet).
    """
    # Read RData into Rpy2 robjects
    r_eSet, r_assayData, r_fData, r_pData = _read_ExpressionSet_RData(RData)
    # Parse assayData, fData, and pData
    exprs = _parse_assayData(r_assayData, assay)
    fData = _parse_rdataframe(r_fData, fFactors)
    pData = _parse_rdataframe(r_pData, pFactors)
    # Add metadata
    kwargs['source'] = RData
    if verbose:
        print "Loading eSet from", RData
        print r_eSet
    return ExpressionSet(exprs, fData, pData, **kwargs)

def HDF52ExpressionSet(HDF5, exprs='exprs', fData='fData', pData='pData', meta='meta', verbose=True):
    """Read HDF file into ExpressionSet.

    HDF5: the input HDF5 path.
    exprs: the name of the exprsstion table .
    fData: the name of the feature table, or None.
    pData: the name of the phenotype table, or None.

    Return an ExpressionSet object.
    """
    store = pd.HDFStore(HDF5)
    hdf_exprs = store[exprs]
    hdf_fData = store[fData] if isinstance(fData, str) else None
    hdf_pData = store[pData] if isinstance(pData, str) else None
    hdf_meta = store[meta]   if isinstance(meta, str)  else {}
    hdf_meta['source'] = HDF5
    if verbose:
        print "Loading dataframes from", HDF5
        print store
    store.close()
    return ExpressionSet(hdf_exprs, hdf_fData, hdf_pData, **hdf_meta)

# ================================================================================
# Output functions
# ================================================================================

def ExpressionSet2RData(eSet, RData, verbose=True):
    """Write ExpressionSet to RData as a single-assay ExpressionSet object

    eSet:  A omics ExpressionSet object
    RData: Output RData filename

    Note: Mutiple assay data currently not supported in this version.
    Todo: Support multiple expresion matrixes into assayData.
    """
    importr('Biobase')
    r.assign("exprs", eSet.exprs)
    r.assign("fdata", eSet.fData)
    r.assign("pdata", eSet.pData)
    r.assign("rdata", RData)
    r("eSet = ExpressionSet(assayData=as.matrix(exprs), \
                            featureData=AnnotatedDataFrame(fdata), \
                            phenoData=AnnotatedDataFrame(pdata))")
    r("save(eSet, file=rdata)")
    if verbose:
        print "Saving eSet to", RData
        print r.eSet

def ExpressionSet2HDF5(eSet, HDF5, verbose=True):
    """Write ExpressionSet to HDF5 as a buch of Pandas dataframes

    eSet:  A omics ExpressionSet object
    HDF5: Output HDF5 filename

    Note: Mutiple assay data currently not supported in this version.
    Todo: Support multiple expresion matrixes into assayData.
    """
    store = pd.HDFStore(HDF5)
    store['exprs'] = eSet.exprs
    if not eSet.fData.empty: store.append('fData', eSet.fData)
    if not eSet.pData.empty: store.append('pData', eSet.pData)
    if not eSet.meta.empty:  store.append('meta',  eSet.meta)
    if verbose:
        print "Saving eSet dataframes to", HDF5
        print store
    store.close()
