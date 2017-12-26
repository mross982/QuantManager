#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
#    Copyright © 2008 Pierre Raybaut
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from __future__ import absolute_import, print_function

import sys
import os
import os.path as osp
from collections import OrderedDict

from six.moves.winreg import (
    OpenKey, EnumValue, QueryInfoKey, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
)
from six.moves import range

from xy.userconfig import UserConfig, get_home_dir
from xy import __version__


DEFAULTS = {
            'startup': 'default.py',
            }

CONF = UserConfig('xy', defaults=DEFAULTS, version=__version__, subfolder='.xy')


def get_conf_path(filename=None):
    """Return absolute path for configuration file with specified filename"""
    conf_dir = osp.join(get_home_dir(), '.xy')
    if not osp.isdir(conf_dir):
        os.mkdir(conf_dir)
    if filename is None:
        return conf_dir
    else:
        return osp.join(conf_dir, filename)


def getreg():
    key = "Software\Python(x,y)"
    regxy = dict()
    try:
        k = OpenKey(HKEY_LOCAL_MACHINE ,key)
    except WindowsError:
        try:
            k = OpenKey(HKEY_CURRENT_USER, key)
        except:
            raise RuntimeError("Python(x,y) is not installed on this computer")
    for i in range(0, QueryInfoKey(k)[1]):
        try:
            j = EnumValue(k, i)
            regxy[j[0]] = j[1]#.replace('\\','/')
        except:
            break
    return regxy

def getplugins():
    key = "Software\Python(x,y)\uninstall"
    regxy = OrderedDict()
    try:
        k = OpenKey(HKEY_LOCAL_MACHINE, key)
    except WindowsError:
        try:
            k = OpenKey(HKEY_CURRENT_USER, key)
        except:
            raise RuntimeError("Python(x,y) is not installed on this computer")
    for i in range(0, QueryInfoKey(k)[1]):
        try:
            j = EnumValue(k, i)
            regxy[j[0]] = j[1]#.replace('\\','/')
        except:
            break
    return regxy


def default_startup():
    filename=osp.join(STARTUP_PATH, CONF.get(None, 'startup'))
    if not osp.exists(filename):
        base = """#!/usr/bin/env python
# -*- coding: latin-1 -*-
# This script was automatically generated

## Loading NumPy
import numpy

## Loading SciPy
import scipy

## Importing all NumPy functions, modules and classes
from numpy import *
"""
        mlab = """
## Importing Mayavi's mlab as 'ml'
from enthought.mayavi import mlab as ml
"""
        f = open(filename,"w")
        f.write(base)
        f.close()
        if osp.exists(osp.join(sys.prefix, "Scripts", "mayavi2.exe")):
            f = open(osp.join(STARTUP_PATH, 'default_with_mlab.py'), "w")
            f.write(base)
            f.write(mlab)
            f.close()


def createdir(path):
    if not osp.exists(path):
        os.mkdir(path)
    return path

STARTUP_PATH = createdir(get_conf_path("startups"))
LOG_PATH = createdir(get_conf_path("logs"))

REGXY = getreg()
DOC_PATH = REGXY['DocPath']
XY_VERSION = REGXY['Version']

PLUGINS = getplugins()

def main():
    print("Python(x,y):")
    print("\tVERSION:", XY_VERSION)
    print("\tDOC_PATH:", DOC_PATH)
    print("PLUGINS:\n\t%s" % "\n\t".join(PLUGINS.keys()))
    
if __name__ == '__main__':
    main()
