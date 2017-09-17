#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python(x,y) unit tests
"""

from __future__ import print_function
import unittest
import sys
from xy.config import PLUGINS

#import faulthandler
#faulthandler.enable()

def run_module_suite(file_to_run=None, extra_args=()):
    import nose
    return nose.run(argv=[''] + list(extra_args) + [file_to_run])


def run_test_silently(testfunc):
    _stdout, _stderr = sys.stdout, sys.stderr
    class IOHandler(object):
        def write(self, text):
            pass
        
        def flush(self):
            pass
            
    sys.stdout, sys.stderr = IOHandler(), IOHandler()
    result = testfunc()
    sys.stdout, sys.stderr = _stdout, _stderr
    return result


def wrap_test(test_func):
    def new_func(self):
        plug = test_func.__name__.split('_', 1)[1]
        if not plug in PLUGINS:
            print("%s not in PLUGINS" % (plug))
        return test_func(self)
    return new_func


class Test(unittest.TestCase):

    @wrap_test
    def test_astropy(self):
        if 'astropy' in PLUGINS:
            import astropy
            #astropy.test()

    @wrap_test
    def test_babel(self):
        if 'babel' in PLUGINS:
            import babel

    @wrap_test
    def test_base_python(self):
        if 'base_python' in PLUGINS:
            import argparse
            import curses
            import faulthandler
            import cdecimal
            import chardet
            import colorama
            import concurrent.futures
            import configparser
            import cov_core
            import coverage
            import dateutil
            import decorator
            import dill
            import enum
            import funcsigs
            import ipaddress
            import jaraco.windows            
            import lockfile
            import mock
            import more_itertools
            import objgraph
            import pathlib
            import pep8
            import py
            import pytz
            import netifaces
            import singledispatch
            import six
            import unittest2
            import yg.lockfile
            
    @wrap_test
    def test_BeautifulSoup4(self):
        if 'BeautifulSoup4' in PLUGINS:        
            import bs4
            res = run_test_silently(lambda: run_module_suite(bs4.__path__[0]))
            self.assert_(res)
            
    @wrap_test
    def test_blosc(self):
        if 'blosc' in PLUGINS:
            import blosc
            run_test_silently(lambda: blosc.test())

    @wrap_test
    def test_bottleneck(self):
        if 'bottleneck' in PLUGINS:
            import bottleneck
            result = run_test_silently(lambda: bottleneck.test(verbose=0))
            self.assert_(result.wasSuccessful())

    @wrap_test
    def test_cffi(self):
        if 'cffi' in PLUGINS:
            import cffi

    @wrap_test
    def test_cvxopt(self):
        if 'cvxopt' in PLUGINS:
            import cvxopt
            
    @wrap_test
    def test_cvxpy(self):
        if 'cvxpy' in PLUGINS:
            import toolz
            import cvxpy
            res = run_test_silently(lambda: run_module_suite(cvxpy.__path__[0]))
            self.assert_(res)

    @wrap_test
    def test_cx_Freeze(self):
        if 'cx_Freeze' in PLUGINS:
            import cx_Freeze
            
    @wrap_test
    def test_Cython(self):
        if 'Cython' in PLUGINS:
            import Cython
        
    @wrap_test
    def test_docutils(self):
        if 'docutils' in PLUGINS:
            import docutils
        
    @wrap_test
    def test_enaml(self):
        if 'enaml' in PLUGINS:
            import atom
            import kiwisolver
            import enaml
        
    @wrap_test
    def test_EnthoughtToolSuite(self):
        if 'EnthoughtToolSuite' in PLUGINS:
            from enthought.mayavi import mlab
        
    @wrap_test
    def test_fabric(self):
        if 'fabric' in PLUGINS:
            import fabric
        
    @wrap_test
    def test_ffnet(self):
        if 'ffnet' in PLUGINS:
            import ffnet

    @wrap_test
    def test_formlayout(self):
        if 'formlayout' in PLUGINS:
            import formlayout
        
    @wrap_test
    def test_freeimage(self):
        if 'freeimage' in PLUGINS:
            import imageio
            import smc.freeimage
            
    @wrap_test
    def test_gdal(self):
        if 'gdal' in PLUGINS:
            import osgeo.gdal
        
    @wrap_test
    def test_gevent(self):
        if 'gevent' in PLUGINS:
            import ujson
            import wsaccel
            import greenlet
            import gevent
            import geventwebsocket

    @wrap_test
    def test_Gnuplot(self):
        if 'Gnuplot' in PLUGINS:
            import Gnuplot
        
    @wrap_test
    def test_grin(self):
        if 'grin' in PLUGINS:
            import grin

    @wrap_test
    def test_guidata(self):
        if 'guidata' in PLUGINS:
            import guidata
            from guidata import tests
        
    @wrap_test
    def test_guiqwt(self):
        if 'guiqwt' in PLUGINS:
            import guiqwt
            from guiqwt import tests
        
    @wrap_test
    def test_h5py(self):
        if 'h5py' in PLUGINS:
            import h5py
        
    @wrap_test
    def test_html5lib(self):
        if 'html5lib' in PLUGINS:
            import datrie
            import html5lib

    @wrap_test
    def test_IPython(self):
        if 'IPython' in PLUGINS:
            import IPython
            import ipdb
        
    @wrap_test
    def test_itk(self):
        if 'itk' in PLUGINS:
            import itk
        
    @wrap_test
    def test_jinja2(self):
        if 'jinja2' in PLUGINS:
            import jinja2
        
    @wrap_test
    def test_lxml(self):
        if 'lxml' in PLUGINS:
            import cssselect
            import BeautifulSoup
            import lxml

    @wrap_test
    def test_mahotas(self):
        if 'mahotas' in PLUGINS:
            import mahotas

    @wrap_test
    def test_mako(self):
        if 'mako' in PLUGINS:
            import beaker
            import mako
            
    @wrap_test
    def test_matplotlib(self):
        if 'matplotlib' in PLUGINS:
            import matplotlib
    
    @wrap_test
    def test_mdp(self):
        if 'mdp' in PLUGINS:
            import mdp
        
    @wrap_test
    def test_modernize(self):
        if 'modernize' in PLUGINS:
            import libmodernize

    @wrap_test
    def test_mx(self):
        if 'mx' in PLUGINS:
            import mx
        
    @wrap_test
    def test_netCDF4(self):
        if 'netCDF4' in PLUGINS:
            import netCDF4
            import netcdftime
        
    @wrap_test
    def test_networkx(self):
        if 'networkx' in PLUGINS:
            import networkx
        
    @wrap_test
    def test_nose(self):
        if 'nose' in PLUGINS:
            import nose
        
    @wrap_test
    def test_numexpr(self):
        if 'numexpr' in PLUGINS:
            import numexpr
        
    @wrap_test
    def test_numpy(self):
        if 'numpy' in PLUGINS:
            import numpy
            result = run_test_silently(lambda: numpy.test(verbose=0))
            self.assert_(result.wasSuccessful())
        
    @wrap_test
    def test_OpenCV(self):
        if 'OpenCV' in PLUGINS:
            import cv2
            import cv2.cv
        
    @wrap_test
    def test_openpyxl(self):
        if 'openpyxl' in PLUGINS:
            import openpyxl

    @wrap_test
    def test_pandas(self):
        if 'pandas' in PLUGINS:
            import pandas

    @wrap_test
    def test_paramiko(self):
        if 'paramiko' in PLUGINS:
            import ecdsa
            import paramiko

    @wrap_test
    def test_patsy(self):
        if 'patsy' in PLUGINS:
            import patsy

    @wrap_test
    def test_PIL(self):
        if 'PIL' in PLUGINS:
            import PIL
    
    @wrap_test
    def test_pip(self):
        if 'pip' in PLUGINS:
            import pip

    @wrap_test
    def test_ply(self):
        if 'ply' in PLUGINS:
            import ply

    @wrap_test
    def test_pp(self):
        if 'pp' in PLUGINS:
            import pp
        
    @wrap_test
    def test_psutil(self):
        if 'psutil' in PLUGINS:
            import psutil

    @wrap_test
    def test_py2exe(self):
        if 'py2exe' in PLUGINS:
            import py2exe

    @wrap_test
    def test_pyasn1(self):
        if 'pyasn1' in PLUGINS:
            import pyasn1
            
    @wrap_test
    def test_pyaudio(self):
        if 'pyaudio' in PLUGINS:
            import pyaudio

    @wrap_test
    def test_pycares(self):
        if 'pycares' in PLUGINS:
            import pycares

    @wrap_test
    def test_pycparser(self):
        if 'pycparser' in PLUGINS:
            import pycparser

    @wrap_test
    def test_pycrypto(self):
        if 'pycrypto' in PLUGINS:
            import Crypto

    @wrap_test
    def test_PycURL(self):
        if 'PycURL' in PLUGINS:
            import pycurl

    @wrap_test
    def test_pydicom(self):
        if 'pydicom' in PLUGINS:
            run_test_silently(lambda: __import__('dicom'))

    @wrap_test
    def test_pygments(self):
        if 'pygments' in PLUGINS:
            import pygments

    @wrap_test
    def test_pygraphviz(self):
        if 'pygraphviz' in PLUGINS:
            import pygraphviz
            
    @wrap_test
    def test_pyhdf(self):
        if 'pyhdf' in PLUGINS:
            import pyhdf
        
    @wrap_test
    def test_PyICU(self):
        if 'PyICU' in PLUGINS:
            import icu

    @wrap_test
    def test_pylint(self):
        if 'pylint' in PLUGINS:
            import pylint
        
    @wrap_test
    def test_pymc(self):
        if 'pymc' in PLUGINS:
            import pymc
            run_test_silently(lambda: pymc.test())
            
    @wrap_test
    def test_PyOpenGL(self):
        if 'PyOpenGL' in PLUGINS:
            import OpenGL
        
    @wrap_test
    def test_pyodbc(self):
        if 'pyodbc' in PLUGINS:
            import pyodbc

    @wrap_test
    def test_pyparallel(self):
        if 'pyparallel' in PLUGINS:
            import parallel
        
    @wrap_test
    def test_pyparsing(self):
        if 'pyparsing' in PLUGINS:
            import pyparsing

    @wrap_test
    def test_PyQt4(self):
        if 'PyQt4' in PLUGINS:
            import PyQt4.QtGui
            import PyQt4.Qsci
        
    @wrap_test
    def test_PyQwt5(self):
        if 'PyQwt5' in PLUGINS:
            import PyQt4.Qwt5
    
    @wrap_test
    def test_pyreadline(self):
        if 'pyreadline' in PLUGINS:
            import readline
        
    @wrap_test
    def test_pyserial(self):
        if 'pyserial' in PLUGINS:
            import serial

    @wrap_test
    def test_pytables(self):
        if 'pytables' in PLUGINS:
            import tables
            # tables.test() - sometimes crashes!
        
    @wrap_test
    def test_pytest(self):
        if 'pytest' in PLUGINS:
            import pytest

    @wrap_test
    def test_pyvisa(self):
        if 'pyvisa' in PLUGINS:
            import pyvisa
        
    @wrap_test
    def test_PyWavelets(self):
        if 'PyWavelets' in PLUGINS:
            import pywt

    @wrap_test
    def test_pywin32(self):
        if 'pywin32' in PLUGINS:
            import win32com, win32api
        
    @wrap_test
    def test_pywinauto(self):
        if 'pywinauto' in PLUGINS:
            import pywinauto

    @wrap_test
    def test_pyyaml(self):
        if 'pyyaml' in PLUGINS:
            import yaml

    @wrap_test
    def test_pyzmq(self):
        if 'pyzmq' in PLUGINS:
            import zmq
            
    @wrap_test
    def test_reportlab(self):
        if 'reportlab' in PLUGINS:
            import reportlab
        
    @wrap_test
    def test_requests(self):
        if 'requests' in PLUGINS:
            import ndg.httpsclient
            import requests

    @wrap_test
    def test_rst2pdf(self):
        if 'rst2pdf' in PLUGINS:
            import aafigure
            import hyphen
            import pdfrw
            import pyPdf
            import PyPDF2
            import svglib
            import xhtml2pdf
            import svg2rlg
            import rst2pdf

    #@wrap_test
    def test_scikitsimage(self):
        if 'scikits.image' in PLUGINS:
            import skimage
            # result = run_test_silently(lambda: skimage.test(verbose=False))
            # self.assert_(result)

    #@wrap_test
    def test_scikits_learn(self):
        if 'scikits-learn' in PLUGINS:
            import pyamg
            import sklearn
            # res = run_test_silently(
                # lambda: run_module_suite(sklearn.__path__[0], ['--exe'])
            # )
            # self.assert_(res)
            # Skip the following test which is heavy:
            
    @wrap_test
    def test_scipy(self):
        if 'scipy' in PLUGINS:
            import scipy
            result = scipy.test(verbose=0)#run_test_silently(lambda: scipy.test(verbose=0))
            self.assert_(result.wasSuccessful())
        
    @wrap_test
    def test_seaborn(self):
        if 'seaborn' in PLUGINS:
            import seaborn

    @wrap_test
    def test_SendKeys(self):
        if 'SendKeys' in PLUGINS:
            import SendKeys

    @wrap_test
    def test_setuptools(self):
        if 'setuptools' in PLUGINS:
            try:
                import ed25519ll
                import certifi
                import keyring
                import wheel
                import wincertstore
                import setuptools
            except AssertionError:
                # Expected AssertionError if py2exe test has already be done
                pass
        
    @wrap_test
    def test_simplejson(self):
        if 'simplejson' in PLUGINS:
            import simplejson
        
    @wrap_test
    def test_sphinx(self):
        if 'sphinx' in PLUGINS:
            import sphinx
        
    @wrap_test
    def test_sqlalchemy(self):
        if 'sqlalchemy' in PLUGINS:
            import tempita
            import alembic
            import sqlalchemy

    @wrap_test
    def test_spyder(self):
        if 'spyder' in PLUGINS:
            import spyderlib
        
    @wrap_test
    def test_statsmodels(self):
        if 'statsmodels' in PLUGINS:
            import statsmodels

    @wrap_test
    def test_sympy(self):
        if 'sympy' in PLUGINS:
            import sympy

    @wrap_test
    def test_tornado(self):
        if 'tornado' in PLUGINS:
            import tornado
            
    @wrap_test
    def test_uncertainties(self):
        if 'uncertainties' in PLUGINS:
            import uncertainties

    @wrap_test
    def test_veusz(self):
        if 'veusz' in PLUGINS:
            import minuit
            import pyemf
            import sampy
            import veusz

    @wrap_test
    def test_virtualenv(self):
        if 'virtualenv' in PLUGINS:
            import virtualenv

    @wrap_test
    def test_vitables(self):
        if 'vitables' in PLUGINS:
            import vitables
        
    @wrap_test
    def test_vpython(self):
        if 'vpython' in PLUGINS:
            import visual
        
    @wrap_test
    def test_vtk(self):
        if 'vtk' in PLUGINS:
            import vtk
        
    @wrap_test
    def test_winpdb(self):
        if 'winpdb' in PLUGINS:
            import winpdb
        
    @wrap_test
    def test_wxPython(self):
        if 'wx' in PLUGINS:
            import wx
        
    @wrap_test
    def test_xlrd(self):
        if 'xlrd' in PLUGINS:
            import xlrd

    @wrap_test
    def test_xlwt(self):
        if 'xlwt' in PLUGINS:
            import xlwt

    @wrap_test
    def test_xy(self):
        if 'xy' in PLUGINS:
            import xy

    # additional plugins

    @wrap_test
    def test_basemap(self):
        if 'basemap' in PLUGINS:
            import basemap

    @wrap_test
    def test_brian(self):
        if 'brian' in PLUGINS:
            import brian

    @wrap_test
    def test_fipy(self):
        if 'fipy' in PLUGINS:
            import fipy

    @wrap_test
    def test_golem(self):
        if 'golem' in PLUGINS:
            import golem

    @wrap_test
    def test_pycuda(self):
        if 'pycuda' in PLUGINS:
            import pycuda

    @wrap_test
    def test_pygame(self):
        if 'pygame' in PLUGINS:
            import pygame


    @wrap_test
    def test_pygrib(self):
        if 'pygrib' in PLUGINS:
            import pygrib

    @wrap_test
    def test_pyopencl(self):
        if 'pyopencl' in PLUGINS:
            import pyopencl
            import pytools

    @wrap_test
    def test_pyproj(self):
        if 'pyproj' in PLUGINS:
            import pyproj

    @wrap_test
    def test_pysparse(self):
        if 'pysparse' in PLUGINS:
            import pysparse

    @wrap_test
    def test_shapely(self):
        if 'shapely' in PLUGINS:
            import shapely

    @wrap_test
    def test_simpleparse(self):
        if 'simpleparse' in PLUGINS:
            import simpleparse

    @wrap_test
    def test_SimPy(self):
        if 'SimPy' in PLUGINS:
            import simpy

    @wrap_test
    def test_unum(self):
        if 'unum' in PLUGINS:
            import unum

    @wrap_test
    def test_visvis(self):
        if 'visvis' in PLUGINS:
            import visvis

def run():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run()
