"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
https://pypi.python.org/pypi?%3Aaction=list_classifiers
"""

from setuptools import setup, find_packages
import omics as pkg  # change 'omics' to your package name

# Get the long description from README.md
with open('README.md') as f:
    long_description = f.read()

setup(
    name=pkg.__name__,
    version=pkg.__version__,
    description=pkg.__doc__.split('\n')[0],
    long_description=long_description,
    url=pkg.__url__,
    author=pkg.__author__,
    author_email=pkg.__email__,
    license=pkg.__license__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='bioinformatics biostatistics genomics',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pandas',
        'rpy2'
    ]
)
