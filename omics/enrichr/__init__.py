"""Module enrichr

Access enrichr function via its API.

Available gene sets: http://amp.pharm.mssm.edu/Enrichr/#stats

Usage:

1. Start an analysis job

>>> job = analyze_gene_list(genes)

2. Download single enrichment result to current location

>>> download_enrichment(job['userListId'], 'KEGG_2016')

3. Download multiple enrichment results at once

>>> genesets = ['Reactome_2016', "ChEA_2015", "OMIM_Disease"]
>>> download_multiple_enrichments(job['userListId'], genesets)

4. Combine enrichment results into one Excel file

>>> combine_results_to_excel(input_files, output_excel_file)

Use run_enrichr() to perform all above steps.

Notes:

Sometimes wrong characters might be in the result file, which will cause
UnicodeDecodeError when writing it to an Excel file. Try to manually fix
the text file and see if it works. For example, there is a term called
"Loss of proteins required for interphase microtubule organization from
the centrosome_Homo sapiens_R-HSA-380284" in Reactome 2016. There is a
0xa0 character between "organization" and "from". You must replace it
with a regular space or it will fail when saving to an Excel file.

Reference: http://amp.pharm.mssm.edu/Enrichr/help#api
"""
import json
import os, os.path
import requests
#import uuid

# Pre-defined gene set lists
genesets = {'pathway': ['KEGG_2016', "Reactome_2016"],
            'GO':      ["GO_Biological_Process_2015",
                        "GO_Cellular_Component_2015",
                        "GO_Molecular_Function_2015"],
            'general': ["KEGG_2016",
                        "Reactome_2016",
                        "ChEA_2015",
                        "ENCODE_TF_ChIP-seq_2015",
                        "ENCODE_Histone_Modifications_2015",
                        "Epigenomics_Roadmap_HM_ChIP-seq",
                        "GO_Biological_Process_2015",
                        "GO_Cellular_Component_2015",
                        "GO_Molecular_Function_2015",
                        "MGI_Mammalian_Phenotype_Level_3",
                        "MGI_Mammalian_Phenotype_Level_4",
                        "Human_Phenotype_Ontology",
                        "dbGaP",
                        "OMIM_Disease",
                        "HomoloGene"]
           }

def analyze_gene_list(genes, description=None):
    """Start a new job to analyze a gene list.

    genes: a list of input genes.
    description: name of the input gene list.

    Return a JSON object with unique job ID, e.g.,
        {"userListId": 363320,
         "shortId": "59lh"}
    """
    ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/addList'
    genes_str = '\n'.join(list(genes))
    description = description if description else "%d input genes" % len(genes)
    payload = {
        'list': (None, genes_str),
        'description': (None, description)
    }
    print "Connecting to enrichr server ...",
    response = requests.post(ENRICHR_URL, files=payload)
    if response.ok:
        print "ok."
        return json.loads(response.text)
    else:
        raise Exception('failed.')

def download_enrichment(user_list_id, gene_set='KEGG_2016', filename=None, output_dir=".", verbose=True):
    """Download enrichment result to a file.

    user_list_id: a job ID connecting to enrichr service.
    gene_set: the name of gene set to use.
    filename: the filename prefix for output file (default: user_list_id).
    output_dir: where to store the output file.
    verbose: silent or not.

    Return the file path of downloaded file.
    """
    ENRICHR_URL = 'http://amp.pharm.mssm.edu/Enrichr/export'
    query_string = '?userListId=%s&filename=%s&backgroundType=%s'

    # filename: space is not allowed; use userListId when no filename provided.
    if not filename:
        #filename = str(uuid.uuid4())
        filename = str(user_list_id)
    filename = "{0}.{1}.txt".format(filename, gene_set).replace(' ', '_')
    path = os.path.join(output_dir, filename)

    url = ENRICHR_URL + query_string % (user_list_id, filename, gene_set)
    response = requests.get(url.replace(' ', '_'), stream=True)

    with open(path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    if verbose:
        print "Output %s enrichment to %s." % (gene_set, path)
    return path

def download_multiple_enrichments(user_list_id, gene_sets, filename=None, output_dir=".", verbose=True):
    """Download mutiple enrichments at once.

    Parameters: See download_enrichment.

    Return a list of output file paths.
    """
    FILES = [download_enrichment(user_list_id, gs, filename, output_dir, verbose) \
             for gs in gene_sets]
    return FILES

def combine_results_to_excel(input_files, output_excel_file, sheet_names=None):
    """Combine enrichment results into one single Excel file.

    input_files: file paths of input files (enrichment result tables).
    output_excel_file: must ends with .xlsx.
    sheet_names: names for sheets. Use input file names when None.

    Return the file path of output Excel file.
    """
    import pandas as pd
    if not sheet_names:
        sheet_names = [os.path.basename(f) for f in input_files]
    with pd.ExcelWriter(output_excel_file) as xls:
        print "<%s>:" % output_excel_file
        for (f, name) in zip(input_files, sheet_names):
            name = name if len(name) < 32 else name[:32]
            print name,
            pd.read_table(f, index_col=0).to_excel(xls, sheet_name=name)
    return output_excel_file

def run_enrichr(genes, genesets, output_excel_file=None, verbose=True):
    """A wrapper function that performs the enrichr pipeline:

    1. Start an analysis job with the input genes.
    2. Download multiple enrichment results at once.
    3. Combine enrichment results into one Excel file.

    Parameters
    ----------

    genes: a list of input genes.
    genesets: the name of gene set to use.
    output_excel_file: must ends with .xlsx; use job ID if None.
    verbose: silence or not.

    Return
    ------

    The file path of combined Excel file.
    """
    job = analyze_gene_list(genes)
    userListId = job['userListId']
    tempdir = "enrichr.%d.temp" % userListId
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)
    if not output_excel_file:
        output_excel_file = "enrichr.%d.combined.xlsx" % userListId
    files = download_multiple_enrichments(userListId, genesets, output_dir=tempdir, verbose=verbose)
    combine_results_to_excel(files, output_excel_file)
