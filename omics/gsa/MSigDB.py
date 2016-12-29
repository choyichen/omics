"""Load MSigDB gene set metadata.
"""
import pandas as pd
import gzip
import xml.etree.ElementTree as ET

XML = '../MSigDB/xml/msigdb_v5.1.xml.gz'
attributes = ['STANDARD_NAME', 'CATEGORY_CODE', 'SUB_CATEGORY_CODE', 'DESCRIPTION_BRIEF'] # 'EXTERNAL_DETAILS_URL'

def xml2df(path, attributes=attributes):
    tree = ET.parse(gzip.open(path))
    root = tree.getroot()
    data = [[gs.attrib[k] for k in attributes] for gs in root.iter('GENESET')]
    df = pd.DataFrame(data, columns=attributes).set_index('STANDARD_NAME')
    return df
