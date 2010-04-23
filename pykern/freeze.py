#!/usr/bin/python
#
# Basic tool to freeze python code.
#
# Freezing is the process of taking a bunch of Python modules, compiling them
# to bytecode, and then outputting them as arrays of bytes suitable for the
# C compiler. This allows modules to be built into the Python interpreter.
#
# This tool is based on freeze.py from the main Python distribution's Tools
# directory, but it's dumber; it doesn't try to resolve dependencies at all
# and simply freezes all *.py files in the directories it is passed as
# arguments. Subdirectories of the given directories are treated as packages,
# but the part of the path given in the argument is ignored (this means that
# multiple root directories can contribute to the same packages).
#
#
# Copyright 2008 Torne Wuff, but loosely based on freeze.py from the main
# Python distribution.
#
# This file is part of Pycorn.
#
# Pycorn is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import os
import sys
import fnmatch
import marshal

# Template bits of C code
header = """\
#include "Python.h"

"""
middle = """
static struct _frozen _PyImport_FrozenModules[] = {
"""
trailer = """\
    {0, 0, 0} /* sentinel */
};

struct _frozen *PyImport_FrozenModules = _PyImport_FrozenModules;
"""

def makefreeze(moddict):
    """Write out a C source code version of a set of compiled modules.

    Given a dictionary which maps module names to a dictionary containing keys
    'code' (the bytecode for the module) and 'package' (a boolean, to mark
    packages), write out frozen.c in the current directory.

    """
    outfp = open('frozen.c', 'w')
    outfp.write(header)
    done = []
    mods = moddict.keys()
    mods.sort()
    for mod in mods:
        m = moddict[mod]
        mangled = "__".join(mod.split("."))
        print "freezing", mod, "..."
        str = marshal.dumps(m['code'])
        size = len(str)
        if m['package']:
            # Indicate package by negative size
            size = -size
        done.append((mod, mangled, size))
        writecode(outfp, mangled, str)
    print "generating table of frozen modules"
    outfp.write(middle)
    for mod, mangled, size in done:
        outfp.write('\t{"%s", M_%s, %d},\n' % (mod, mangled, size))
    outfp.write('\n')
    outfp.write(trailer)
    outfp.close()

def writecode(outfp, mod, str):
    """Write out a single module's bytecode as a C array"""
    outfp.write('static unsigned char M_%s[] = {' % mod)
    for i in range(0, len(str), 16):
        outfp.write('\n\t')
        for c in str[i:i+16]:
            outfp.write('%d,' % ord(c))
    outfp.write('\n};\n')

# dictionary of modules to freeze
mods = {}

def addfile(path, shortpath, namelist):
    """Add the given file to the dictionary of modules to freeze."""
    package = False
    if namelist[-1] == "__init__":
        package = True
        del namelist[-1]
    modname = '.'.join(namelist)
    f = open(path)
    text = f.read() + '\n'
    f.close()
    code = compile(text, shortpath, "exec")
    mods[modname] = {'code': code, 'package': package}

def scandir(dir, shortdir, modprefix):
    """Recursively scan a directory looking for modules to freeze."""
    for entry in os.listdir(dir):
        path = os.path.join(dir, entry)
        shortpath = os.path.join(shortdir, entry)
        if os.path.isdir(path):
            scandir(path, shortpath, modprefix + [entry])
        elif os.path.isfile(path) and fnmatch.fnmatch(entry, '*.py'):
            addfile(path, shortpath, modprefix + [entry[:-3]])

for dir in sys.argv[1:]:
    scandir(dir, "", [])

makefreeze(mods)
