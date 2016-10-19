"""Expression module
"""
# The core class
from .ExpressionSet import ExpressionSet

# I/O tools
from ..io.ExpressionSetIO import RData2ExpressionSet
from ..io.ExpressionSetIO import HDF52ExpressionSet
from ..io.ExpressionSetIO import ExpressionSet2RData
from ..io.ExpressionSetIO import ExpressionSet2HDF5
