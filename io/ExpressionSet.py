"""R's ExpressionSet <-> Pandas DataFrames -> HDF5 storage

Usage:
  * ExpressionSet2DataFrames(RData, assay=None, fFactors='auto', pFactors='auto')
  * ExpressionSet2HDF5(RData, HDF5, **kwargs)
  * DataFrames2ExpressionSet(exprs, fData, pData, RData)

Note:
  * ExpressionSet should be the only object in the input RData

Ref:
  * http://pandas.pydata.org/pandas-docs/stable/r_interface.html
  * https://www.bioconductor.org/packages/release/bioc/vignettes/Biobase/inst/doc/ExpressionSetIntroduction.pdf
"""
import readline
import pandas as pd
from rpy2.robjects import r
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

__author__ = "Cho-Yi Chen"

importr('Biobase')
pandas2ri.activate()

def _read_ExpressionSet(RData):
    """Read ExpressionSet RData into Rpy2 robjects

    RData: Path to an RData file

    Return assayData, featureData, phenotypeData.

    Note: Assume ExpressionSet is the only object in the RData.
    """
    print "Loading RData from", RData
    eSet = r.load(RData)
    obj = r.get(eSet)
    assayData = r.assayData(obj)  # rpy2 environment object
    fData = r.fData(obj)          # rpy2 DataFrame object
    pData = r.pData(obj)          # rpy2 DataFrame object
    print r.obj
    return assayData, fData, pData

def _write_ExpressionSet(exprs, fData, pData, RData):
    """Write dataframes to RData as a single-assay ExpressionSet object

    exprs: The 'exprs' expression df/matrix required for assayData in an ExpressionSet
    fData: Gene feature table
    pData: Sample phenotype table
    RData: Output path

    Note: 1. The genes/samples should be aligned between all input dataframes.
          2. Mutiple assay data currently not supported in this version.
    Todo: Support multiple elements into assayData.
    """
    print "Saving RData to", RData
    r.assign("exprs", exprs)
    r.assign("fdata", fData)
    r.assign("pdata", pData)
    r.assign("rdata", RData)
    r("eSet = ExpressionSet(assayData=as.matrix(exprs), featureData=AnnotatedDataFrame(fdata), phenoData=AnnotatedDataFrame(pdata))")
    r("eSet")
    r("save(eSet, file=rdata)")

def _parse_assayData(assayData, assay=None):
    """Parse Rpy2 assayData (Environment object)

    assayData: Rpy2 Environment object.
    assay: An assay name or a list of assay names to be loaded. Set None to inclue all.

    Return a dict of assay-name-to-assay-dataframe (pandas) mapping.
    """
    # assays to be included
    if isinstance(assay, str):
        assays = [assay]
    elif assay is None:
        assays = assayData.keys()
    else:
        assays = assay

    # parse assays one-by-one
    D = {}
    print 'assayData'
    for k in assays:
        mat = assayData[k]
        data = pandas2ri.ri2py(mat)
        genes = pandas2ri.ri2py(r.rownames(mat))
        samples = pandas2ri.ri2py(r.colnames(mat))
        df = pd.DataFrame(data, index=genes, columns=samples)
        D[k] = df
        print '\t%s: %d features, %d samples' % (k, len(genes), len(samples))
    return D

def _parse_rdf(rdf, categorical_columns='auto'):
    """Parse Rpy2 DataFrame

    rdf: Rpy2 DataFrame object.
    categorical_columns: A list of column names indicating categorical data.
      If 'auto', categorical columns will be determined by their contents, individually.
      If None, do nothing and use the default dtypes.

    Return a pandas dataframe.
    """
    df = pandas2ri.ri2py(rdf)

    if categorical_columns == 'auto':
        # Infer if there are categorical data
        n = df.shape[0]
        subdf = df.select_dtypes(include=['integer', 'object'])
        categorical_columns = [k for k,v in subdf.iteritems() if n > 10 * len(set(v))]

    if categorical_columns:
        # Make each column categorical
        assert not isinstance(categorical_columns, str)
        for k in categorical_columns:
            df[k] = df[k].astype('category')

    print df.index
    return df

def ExpressionSet2DataFrames(RData, assay=None, fFactors='auto', pFactors='auto'):
    """ExpressionSet (RData) to pandas dataframes

    RData: Path to an RData file
    assay: Assay name or a list of assay names to be loaded. Set None to inclue all.
    f/pFactors: List of column names indicating categorical data.
      If 'auto', categorical columns will be determined by their contents, individually.
      If None, do nothing and use the default dtypes.

    Return assay dataframs, feature dataframe, phenotype dataframe.
    """
    # Read RData into Rpy2 robjects
    assayData, fData, pData = _read_ExpressionSet(RData)

    # Parse assayData, fData, and pData
    print "--->\n"
    assay_dfs = _parse_assayData(assayData, assay)
    feature_df = _parse_rdf(fData, fFactors)
    phenotype_df = _parse_rdf(pData, pFactors)
    return assay_dfs, feature_df, phenotype_df

def ExpressionSet2HDF5(RData, HDF5, **kwargs):
    """ExpressionSet (RData) to HDF5 (pandas dataframes)

    RData: Path to the input RData file
    HDF5: Path for output HDF5 file
    kwargs: Keyword arguments to pass to ExpressionSet2DataFrames
    """
    # Write dataframes to HDF5
    assayData, fData, pData = ExpressionSet2DataFrames(RData, **kwargs)

    # Writer
    print "Writing dataframes to", HDF5
    store = pd.HDFStore(HDF5)
    for name, data in assayData.iteritems():
        store[name] = data
        print '\t%s: %d features, %d samples' % (name, data.shape[0], data.shape[1])
    store.append('fData', fData)
    print '\tfData: %d features, %d variables' % (fData.shape[0], fData.shape[1])
    store.append('pData', pData)
    print '\tpData: %d samples, %d variables' % (pData.shape[0], pData.shape[1])
    store.close()

def DataFrames2ExpressionSet(exprs, fData, pData, RData):
    """Write dataframes to RData as a single-assay ExpressionSet object

    exprs: The 'exprs' df required for assayData in an ExpressionSet
    fData: Gene feature df
    pData: Sample phenotype df
    RData: Output RData path

    Return an Rpy2 eSet object.

    Note: 1. The genes/samples should be aligned between all input dataframes.
          2. Mutiple assay data currently not supported in this version.
    Todo: Support multiple elements into assayData.
    """
    # Check if dataframes are aligned
    assert all(exprs.index == fData.index)
    assert all(exprs.columns == pData.index)

    print "%d features x %d samples" % (exprs.shape[0], exprs.shape[1])
    print "%d feature attributes" % fData.shape[1]
    print "%d phenotype variables" % pData.shape[1]
    _write_ExpressionSet(exprs, fData, pData, RData)

