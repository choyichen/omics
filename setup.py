"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

setup(
    name='omics',
    # See https://packaging.python.org/distributing/#version
    version='0.1.0',
    description='A Python package for omics data analysis.',
    url='https://github.com/choyichen/omics',
    author='Cho-Yi (Joey) Chen',
    author_email='ntu.joey@gmail.com',
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
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
