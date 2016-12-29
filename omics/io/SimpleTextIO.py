"""I/O functions for simple text files.
"""
__author__ = "Cho-Yi Chen"
__version__ = "2016.12.28"

def file2list(path, dtype=None):
    """Every line in the file becomes a string in a list.
    """
    L = open(path).read().splitlines()
    return map(dtype, L) if dtype else L

def file2set(path, dtype=None):
    """Every line in the file becomes a string in a set.
    """
    return set(file2list(path, dtype))

def list2file(L, path, low_memory=False):
    """Every string in the list L becomes a line in a file.
    """
    with open(path, 'w') as fout:
        if low_memory:
            fout.writelines("%s\n" % line for line in L)
        else:
            fout.write('\n'.join(L))

def set2file(S, path, low_memory=False):
    """Every string in the set S becomes a line in a file.
    """
    return list2file(sorted(list(S)), path, low_memory=low_memory)

