"""Module biomaRt - Interface to utilize Bioconductor's biomaRt package in R.

Command line Usage:

./biomaRt.py -
./biomaRt.py genes.txt
cat genes.txt | ./biomaRt.py

Ref: https://bioconductor.org/packages/release/bioc/html/biomaRt.html
Version: http://www.ensembl.org/info/website/archives/assembly.html
"""
import sys
import pandas as pd
import readline  # current conda version needs this to import rpy2
import rpy2
from rpy2.robjects.packages import importr
from rpy2.robjects import pandas2ri

__author__ = 'Cho-Yi Chen (ntu.joey@gmail.com)'
__version__ = '16.11.13'

class BioMart:
    """BioMart service.

    A wrapper class that provides interface to Bioconductor's biomaRt package in R.

    Usage:

    >>> values = ["ENSG00000258484", "ENSG00000149531"]
    >>> mart = BioMart(version=74)
    >>> df = mart.getBM(values, "ensembl_gene_id", ["ensembl_gene_id", "hgnc_symbol"])
    >>> df
       ensembl_gene_id hgnc_symbol
    1  ENSG00000149531       FRG1B
    2  ENSG00000258484      SPESP1

    >>> df = mart.getBM("Y", "chromosome_name", ["ensembl_gene_id", "hgnc_symbol", "chromosome_name"])
    >>> df.head(3)
       ensembl_gene_id hgnc_symbol chromosome_name
    1  ENSG00000226555       AGKP1               Y
    2  ENSG00000228787  NLGN4Y-AS1               Y
    3  ENSG00000236131     MED13P1               Y

    Notes:

    Rows returned by getBM are sorted by "filter", and could be in different order than in the "values" argument.
    You can use "df.set_index(filter).loc[values]" to make sure it follows the order of the input values.

    When calling getBM(), make sure the filter variable to use is in the attribute list.
    """

    def __init__(self, biomart="ensembl", dataset="hsapiens_gene_ensembl",\
                       host=None, version=None, verbose=False):
        """Initialize a BioMart object by connecting to a BioMart service.

        If host and version are not specified, it will use the current build.
        """
        self.base = importr('biomaRt')
        if version:
            # version specified, use that archived mart
            self.mart = self.base.useEnsembl(biomart, dataset, version=version, verbose=verbose)
        elif host:
            # host specified, use the host
            self.mart = self.base.useEnsembl(biomart, dataset, host=host, verbose=verbose)
        else:
            # use biomaRt default (host="www.ensembl.org")
            self.mart = self.base.useEnsembl(biomart, dataset, verbose=verbose)

    def listAttributes(self):
        print self.base.listAttributes(self.mart)

    def listDatasets(self):
        print self.base.listDatasets(self.mart)

    def listEnsembl(self):
        print self.base.listEnsembl(self.mart)

    def listFilters(self):
        print self.base.listFilters(self.mart)

    def listMarts(self):
        print self.base.listMarts(self.mart)

    def getBM(self, values, filters="hgnc_symbol",\
                    attributes=["ensembl_gene_id", "hgnc_symbol", "external_gene_id",\
                                "chromosome_name", "gene_biotype", "description"]):
        """Retrieves information from the BioMart database.

        Attributes are the identifiers that you want to retrieve. For example HGNC gene ID, chromosome name, Ensembl transcript ID.
        Filters are the identifiers that you supply in a query. Some but not all of the filter names may be the same as the attribute names.
        Values are the filter identifiers themselves. For example the values of the filter "HGNC symbol" could be 3 genes "TP53", "SRY" and "KIAA1199".

        Return query result as a Pandas DataFrame object.
        """
        assert filters in attributes
        df = self.base.getBM(attributes=attributes, filters=filters, values=values, mart=self.mart)
        return pandas2ri.ri2py(df)

    #def getGene(self, id="ENSG0000022549", type="ensembl_gene_id"):
        #"""Not working in this version...
        #"""
        #print self.base.getGene(id=id, type=type, mart=self.mart)
        #print "Unimplemented: This method doesn't work at all..."""


# ==============================================================================
# Functions
# ==============================================================================

def query(values, filters, version=74, attributes=["hgnc_symbol", "external_gene_id", "chromosome_name", "gene_biotype", "description"]):
    """A shortcut wrapper to query a list of values (genes).
    """
    mart = BioMart(version=version)
    if filters not in attributes:
        attributes.insert(0, filters)
    df = mart.getBM(values, filters, attributes)
    return df.set_index(filters).loc[values]


def annotate(genes, version=74, verbose=False):
    """A shortcut wrapper to annotate a list of genes (Entrez Gene ID/Ensembl Gene ID/HGNC Symbol).
    """
    if genes[0].isdigit():
        filters = 'entrez_gene_id'
    elif genes[0].startswith("ENSG"):
        filters = 'ensembl_gene_id'
    else:
        filters = 'hgnc_symbol'
    df = query(genes, filters, version)
    if verbose == True:
        print df
    return df

# ==============================================================================
# Testing
# ==============================================================================

if __name__ == "__main__":
    import doctest
    doctest.testmod()

