"""GeneSetCollection class.
"""
import os.path
import pandas as pd

__author__ = "Cho-Yi Chen"
__version__ = "2016.10.16"

class GeneSetCollection(object):
    """A collection of gene sets.

    * Load GMT file via GeneSetCollection(GMT).
    * Search(gene): Input a gene, list all gene sets containing the input gene (symbol).
    * Enrichment(genes): Input a gene list, get enrichment results against all gene sets in the collection.

    >>> GMT = "/ifs/labs/cccb/projects/share/MSigDB/gmt/c2.cp.kegg.v5.1.symbols.gmt"
    >>> gmt = GeneSetCollection(GMT)

    >>> gmt
    c2.cp.kegg.v5.1.symbols.gmt: 186 gene sets

    >>> 'KEGG_CELL_CYCLE' in gmt
    True

    >>> gmt.search('CCNB3')
    ['KEGG_P53_SIGNALING_PATHWAY', 'KEGG_PROGESTERONE_MEDIATED_OOCYTE_MATURATION', 'KEGG_CELL_CYCLE']

    >>> df = gmt.enrichment(['PER1', 'PER2', 'PER3', 'CLOCK', 'CRY1', 'CRY2', 'ARNTL', 'TP53'])
    >>> df[df.FDR < 0.05].index
    Index([u'KEGG_CIRCADIAN_RHYTHM_MAMMAL'], dtype='object', name=u'Name')
    """
    def __init__(self, input_file_path):
        self.source = input_file_path
        if input_file_path.endswith(".gmt"):
            self.genesets = self._load_gmt(input_file_path)
        else:
            raise e, 'Unsupported file format.'

    def __str__(self):
        return '{}: {} gene sets'.format(os.path.basename(self.source), len(self.genesets))

    def __repr__(self):
        return self.__str__()

    def __contains__(self, geneset):
        return geneset in self.genesets

    def _load_gmt(self, path):
        D = {}  # a gene_set_name-to-gene_set dict
        for line in open(path):
            L = line.strip().split('\t')
            name = L[0]
            genelist = L[2:]
            D[name] = set(genelist)
        return D

    def search(self, gene):
        return [key for key, geneset in self.genesets.iteritems() if gene in geneset]

    def enrichment(self, genes, background=None, min_size=10, max_size=500):
        from scipy.stats import fisher_exact
        from statsmodels.stats.multitest import multipletests
        # Make sure the input gene list is a set
        if not isinstance(genes, set):
            genes = set(genes)
        # Get consensus background
        self.background = set.union(*self.genesets.values())
        if background is None:
            background = self.background
        else:
            background = set(background) & self.background
        # Fisher exact test for genes against gene sets
        nu = genes & background
        b = len(nu)
        d = len(background)
        out = []
        for name, geneset in self.genesets.iteritems():
            if min_size <= len(geneset) <= max_size:
                nv = geneset & background
                a = len(nu & nv)
                c = len(nv)
                odds, pval = fisher_exact([[a, b-a], [c-a, d-b-c+a]])
                out.append([name, a, b, c, odds, pval])
        df = pd.DataFrame(out, columns=['Name', 'Hits', 'Input', 'Size', 'OddsRatio', 'PValue']).set_index('Name')
        df['FDR'] = multipletests(df['PValue'], method='fdr_bh')[1]
        return df

if __name__ == "__main__":
    import doctest
    doctest.testmod()
