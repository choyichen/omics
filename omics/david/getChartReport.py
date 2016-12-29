#! /usr/bin/env python
"""Methods for generation of DAVID functional chart report.

Adapted from http://david.abcc.ncifcrf.gov/content.jsp?file=DAVID_WebService.html

Some Limitations:
  * A job with >3000 genes to generate gene or term cluster report will not be handled by DAVID due to resource limit.
  * No more than 200 jobs in a day from one user or computer.

Author: Cho-Yi Chen (ntu.joey@gmail.com)
Date: 2013/4/15
"""

def getChartReport(listF, idType, bgF='', resF='', bgName='Background1', listName='List1', category='', thd=0.1, ct=2):
    """Generate DAVID Functional Annotation Chart Report using Web Service.

    listF -- a gene list (a line-separated gene list file or a list of id strings)
    idType -- the type of id used in gene list file (e.g., ENTREZ_GENE_ID, GENE_SYMBOL)
           see http://david.abcc.ncifcrf.gov/content.jsp?file=DAVID_API.html
    bgF -- a background gene list (leave empty to use default background)
    resF -- output result file
         (levae empty to generate a default filename using listF path or listName)
    bgName -- name of background list if bgF specified
    listName -- name of gene list if you want to reuse the list
    category -- a string with category names delimited by commas
             (leave empty to use default categories)
             (see http://david.abcc.ncifcrf.gov/content.jsp?file=DAVID_API.html)
    thd -- the threshold of EASE
    ct -- the threshold of gene count

    Output: written to a chart report text file.
    """
    from suds.client import Client
    import os
    EMAIL = 'd99b48001@ntu.edu.tw'  # should be a registered mail account

    # create a DAVID web service client using the wsdl
    print 'Connecting to DAVID Web Service ...'
    client = Client('http://david.abcc.ncifcrf.gov/webservice/services/DAVIDWebService?wsdl')
    print 'Service authenticating using %s ...' % EMAIL,
    print client.service.authenticate(EMAIL)

    # listF can be a text file path (one id per line) or a list of id strings
    if isinstance(listF, str) and os.path.exists(listF):
        inputListIds = ','.join(open(listF).read().split('\n'))
        print 'Gene list file loaded:', listF
        print '<%s>: %d instances' % (listName, len(open(listF).readlines()))
    else:  # should be iterable
        inputListIds = ','.join(listF)
        print 'Gene list loaded.'
        print '<%s>: %d instances' % (listName, len(listF))
    print 'Percentage mapped (list):', client.service.addList(inputListIds, idType, listName, 0)

    # use of background file (optional)
    flagBg = False
    if bgF and isinstance(bgF, str) and os.path.exists(bgF):
        inputBgIds = ','.join(open(bgF).read().split('\n'))
        print 'Background list file loaded:', bgF
        print '<%s>: %d instances' % (bgName, len(open(inputBgIds).readlines()))
        flagBg = True
    elif bgF:  # should be iterable
        inputBgIds = ','.join(bgF)
        print 'Background list loaded.'
        print '<%s>: %d instances' % (bgName, len(bgF))
        flagBg = True
    if flagBg:
        print 'Percentage mapped (background):', client.service.addList(inputBgIds, idType, bgName, 1)

    # assign categories & get the chart report
    #print 'All available annotation categories:', client.service.getAllAnnotationCategoryNames()
    if category == '':
        print 'Use default categories:', client.service.getDefaultCategoryNames()
    else:
        print 'Use categories:', client.service.setCategories(category)
    chartReport = client.service.getChartReport(float(thd), ct)
    chartRow = len(chartReport)
    print 'Total chart records:',chartRow
    
    # prepare output file
    if resF == '' or not os.path.exists(resF):
        if isinstance(listF, str) and os.path.exists(listF):
            resF = listF + ('.wBG.chartReport.tsv' if flagBg else '.chartReport.tsv')
        else:
            resF = listName + ('.wBG.chartReport.tsv' if flagBg else '.chartReport.tsv')
    with open(resF, 'w') as fOut:
        fOut.write('Category\tTerm\tCount\t%\tPvalue\tGenes\tList Total\tPop Hits\tPop Total\tFold Enrichment\tBonferroni\tBenjamini\tFDR\n')
        for row in chartReport:
            rowDict = dict(row)
            categoryName = str(rowDict['categoryName'])
            termName = str(rowDict['termName'])
            listHits = str(rowDict['listHits'])
            percent = str(rowDict['percent'])
            ease = str(rowDict['ease'])
            Genes = str(rowDict['geneIds'])
            listTotals = str(rowDict['listTotals'])
            popHits = str(rowDict['popHits'])
            popTotals = str(rowDict['popTotals'])
            foldEnrichment = str(rowDict['foldEnrichment'])
            bonferroni = str(rowDict['bonferroni'])
            benjamini = str(rowDict['benjamini'])
            FDR = str(rowDict['afdr'])
            rowList = [categoryName,termName,listHits,percent,ease,Genes,listTotals,popHits,popTotals,foldEnrichment,bonferroni,benjamini,FDR]
            fOut.write('\t'.join(rowList)+'\n')
        print 'Writing to file:', resF
        print

if __name__ == '__main__':
    # usage demo
    getChartReport(listF = './demo/list1.txt', \
                idType = 'AFFYMETRIX_3PRIME_IVT_ID',
                category = 'BBID,BIOCARTA,COG_ONTOLOGY,INTERPRO,KEGG_PATHWAY,OMIM_DISEASE,PIR_SUPERFAMILY,SMART,SP_PIR_KEYWORDS,UP_SEQ_FEATURE')

