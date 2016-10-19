"""Expression module
"""
# The core class
from .ExpressionSet import ExpressionSet

# I/O tools
from omics.io.ExpressionSetIO import RData2ExpressionSet
from omics.io.ExpressionSetIO import HDF52ExpressionSet
from omics.io.ExpressionSetIO import ExpressionSet2RData
from omics.io.ExpressionSetIO import ExpressionSet2HDF5
