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

from PyQt4.QtGui import QApplication, QMessageBox, QFileDialog, QIcon
import os.path as osp
import time, sys, os

LIBPATH = osp.join(sys.prefix,'Lib')

def optimize(path):
    assert osp.exists(path) and osp.isdir(path)
    batfile = 'optimize_temp.bat'
    f=open(batfile,'w')
    f.write('python -O "%s\compileall.py" "%s"' % (LIBPATH,path) )
    f.close()
    os.startfile(batfile)
    time.sleep(3)
    os.remove(batfile)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(osp.dirname(__file__)+'/img/pyc.png'))
    directory = QFileDialog.getExistingDirectory(None,"Select directory to optimize",osp.join(LIBPATH,'site-packages'))
    if not directory.isEmpty() and QMessageBox.question(None, "Optimize",
                                       "Do you really want to compile all .py files to .pyo in the following directory?"+"\n\n"+directory,
                                       QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
        optimize(directory)

if __name__ == "__main__":
    if len(sys.argv)>1:
        optimize(sys.argv[1])
    else:
        main()
