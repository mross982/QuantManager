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

import IPython.ipapi
ip = IPython.ipapi.get()

import ipy_defaults

import os.path as osp

from xy.config import CONF, STARTUP_PATH, LOG_PATH, XY_VERSION, default_startup


def run(filename=None):
    
    if filename is None:
        filename = CONF.get(None, 'startup')
    
    if not filename.endswith('.py'):
        filename+='.py'
    
    default_startup()
    if not osp.exists(osp.join(STARTUP_PATH, filename)):
        filename='default.py'
    
    print "Executing Python(x,y)", XY_VERSION,
    print "profile startup script:", filename
    filename = osp.join(STARTUP_PATH, filename)    

    f = open(filename)
    comment = ""
    for line in f:
        line = line.strip()
        if line[:1] != "#!" and line[:2] != "# -" and line[:1] != "# " and len(line) > 2:
            if line.startswith("##"):
                comment = "  "+line.replace("\n", "").replace("#", "").strip()
            else:
                try:
                    if len(comment) > 0:
                        print comment
                    ip.ex(line)
                    comment = ""
                except StandardError, e:
                    print "    [!]", e
    f.close()

    import time
    try:
        filename = osp.join(LOG_PATH, time.strftime('%Y-%m-%d')+".py")
        notnew=osp.exists(filename)
        ip.IP.logger.logstart(logfname=filename, logmode='append')
        if notnew:
            ip.IP.logger.log_write("# =================================")
        else:
            ip.IP.logger.log_write("""#!/usr/bin/env python
# -*- coding: latin-1 -*-

# %s.py
# Python(x,y) automatic logging file
""" % time.strftime('%Y-%m-%d'))
        ip.IP.logger.log_write("""
#   %s
# =================================""" % time.strftime('%H:%M'))
        print "  Logging to "+filename
    except RuntimeError:
        print "  Already logging to "+ip.IP.logger.logfname

    print ""

