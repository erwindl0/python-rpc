###
# Copyright 2011 Diamond Light Source Ltd.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

'''
Wrapper of plotting functionality in DAWN
'''

import os
import sys

if os.name == 'java':
    import jython.jyplot as _plot
    _plot_set_port = _plot.setremoteport
    import jython.jycore as _core #@Reimport @UnusedImport
    import jython.jybeans as _beans #@Reimport @UnusedImport
else:
    import python.pyplot as _pyplot
    _plot_set_port = _pyplot.setremoteport
    _plot = _pyplot.plotter()
    import python.pycore as _core #@Reimport
    import python.pybeans as _beans #@Reimport

_plot_line = _plot.plot_line
_plot_addline = _plot.plot_addline
_plot_updateline = _plot.plot_updateline
_plot_image = _plot.plot_image
_plot_images = _plot.plot_images
_plot_surface = _plot.plot_surface
_plot_stack = _plot.plot_stack
_plot_updatestack = _plot.plot_updatestack
_plot_points2d = _plot.plot_points2d
_plot_updatepoints2d = _plot.plot_updatepoints2d
_plot_points3d = _plot.plot_points3d
_plot_updatepoints3d = _plot.plot_updatepoints3d
_plot_scanforimages = _plot.plot_scanforimages 
_plot_viewnexustree = _plot.plot_viewnexustree
_plot_volume = _plot.plot_volume

_plot_createaxis = _plot.plot_createaxis
_plot_renameactiveaxis = {'x':_plot.plot_renameactivexaxis, 'y':_plot.plot_renameactiveyaxis}

_plot_clear = _plot.plot_clear
_plot_export = _plot.plot_export

__orders = _plot.plot_orders

_exception = _beans.exception
parameters = _beans.parameters
plotmode = _beans.plotmode
_guibean = _beans.guibean
bean = _guibean
axismapbean = _beans.axismapbean
datasetwithaxisinformation = _beans.datasetwithaxisinformation
databean = _beans.databean

_plot_getbean = _plot.plot_getbean
_plot_setbean = _plot.plot_setbean
_plot_getdatabean = _plot.plot_getdatabean
_plot_setdatabean = _plot.plot_setdatabean

getguinames = _plot.plot_getguinames
window_manager = _plot.plot_window_manager

try:
    import io as _io
    
    _REMOTEVOLNAME = "Remote Volume Viewer"

    def volume(v, name=_REMOTEVOLNAME):
        '''Plot a volume dataset in remote volume view
        '''
        import tempfile
        import os #@Reimport
        tmp = tempfile.mkstemp('.dsr') # '/tmp/blah.dsr'
        os.close(tmp[0])
        vdatafile = tmp[1]
        # convert to byte, int or float as volume viewer cannot cope with boolean, long or double datasets
        if v.dtype == _core.bool:
            v = _core.cast(v, _core.int8)
        elif v.dtype == _core.int64:
            v = _core.cast(v, _core.int32)
        elif v.dtype == _core.float64 or v.dtype == _core.complex64 or v.dtype == _core.complex128:
            v = _core.cast(v, _core.float32)
        _io.save(vdatafile, v, format='binary')
        _plot_volume(name, vdatafile)
        os.remove(vdatafile)

except Exception, e:
    print >> sys.stderr, "Could not import io for volume renderer, this part of plotting will not work"
    print >> sys.stderr, e

import roi


_toList = _core.toList

_PVNAME = "Plot 1"

def setdefname(name):
    '''Assign a default plot view name used by all plotters
    This default name starts as "Plot 1"
    '''
    global _PVNAME
    _PVNAME = name
    
def setremoteport(rpcport=0, rmiport=0):
    '''Connect over RMI or Analysis RPC to the given port.
       If RMI is used (default in Jython for SDS) rpcport is ignored.
       If Analysis RPC is used (default in Python) rmiport is ignored.
       If CORBA is used, both rpc and rmi ports are ignored.
       Values of 0 mean use the default port.'''
    _plot_set_port(rpcport=rpcport, rmiport=rmiport)
    
def _order(order):
    try:
        return __orders[order]
    except KeyError:
        raise ValueError, "Given order not one of none, alpha, chrono"    

def clear(name=None):
    '''Clear plot

    Argument:
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    _plot_clear(name)

_FILE_TYPES = ["PNG/JPEG File", "Postscript File", "SVG File"]

def export(name=None, format=None, savepath=None):
    '''Export plot to svg, png, jpg, ps

    Argument:
    name -- name of plot view to use (if None, use default name)
    format -- format of the file to export to: can be 'svg', 'png', 'jpg' or 'ps' (if None, svg is used by default)
    savepath -- full path and filename of the file to export to (if none, the filename will be 'exported.svg')
    '''
    if name is None:
        name = _PVNAME
    if format is "svg" or format is "SVG" or format is None:
        format = _FILE_TYPES[2]
    if format is "ps" or format is "PS" or format is "eps" or format is "EPS":
        format = _FILE_TYPES[1]
    if format is "PNG" or format is "png" or format is "JPG" or format is "jpg":
        format = _FILE_TYPES[0]
    if savepath is None:
        savepath = "exported.svg"

    _plot_export(name, format, savepath)

'''
Store a global list of x and y axes names in a per-horizontal/vertical dictionary per plot name
'''
_DEF_NAMES = {'x':'X-Axis', 'y':'Y-Axis'}

_AXES_NAMES = { 'x':{}, 'y':{} }

import types as _types

def _parselinearg(x, y, title, name):
    '''x and y can be lists of arrays or single-item dicts (each dict comprises an axis name (or tuple) and array)
    '''
    if y is None:
        if isinstance(x, dict):
            yl = [x]
        else:
            yl = _toList(x)
        xl = None
    else:
        if isinstance(y, dict):
            yl = [y]
        else:
            yl = _toList(y)
        if x is None:
            xl = None
        else:
            if isinstance(x, dict):
                xl = [x]
            else:
                xl = _toList(x)
            if len(xl) == 1:
                x = xl[0]
                if type(x) is _types.DictType: # has axis name
                    x = x.values()[0]
                xLength = x.shape[0]
                for i in yl:
                    if type(i) is _types.DictType: # has axis name
                        i = i.values()[0]
                    if xLength != i.shape[0]:
                        raise AttributeError("length of y does not match the length of x" )
            elif len(xl) != len(yl):
                raise ValueError("number of x datasets should be equal to number of y datasets")
            else:
                for i,j in zip(xl,yl):
                    if type(i) is _types.DictType: # has axis name
                        i = i.values()[0]
                    if type(j) is _types.DictType: # has axis name
                        j = j.values()[0]
                    if i.shape[0] != j.shape[0]:
                        raise AttributeError("length of y does not match the length of x")

    return name, title, xl, yl

_AXES_SIDES = { 'x':{'default':_plot.axis_bottom, 'top':_plot.axis_top, 'bottom':_plot.axis_bottom},
              'y':{'default':_plot.axis_left, 'left':_plot.axis_left, 'right':_plot.axis_right} }

def _setup_axes(al, dirn, name):
    c = 0 # count use of default axis
    for a in al:
        if type(a) is _types.DictType: # has axis name
            n = a.keys()[0]
            if type(n) is _types.TupleType: # has side info
                n = n[0]
            if n == _DEF_NAMES[dirn]:
                c += 1
        else:
            c += 1

    rename = c == 0
    an = []
    for a in al:
        if type(a) is _types.DictType: # has axis name
            n = a.keys()[0]
            rename, n = _setup_axis(rename, n, dirn, name)
            an.append(n)
        else:
            an.append(_DEF_NAMES[dirn])
    return an

def _setup_axis(rename, n, dirn, name):
    '''
    n is axis name (or axis name and side)
    '''
    if type(n) is _types.TupleType: # has side info
        s = _AXES_SIDES[dirn][n[1]]
        n = n[0]
    else:
        s = _AXES_SIDES[dirn]['default']
    al = _AXES_NAMES[dirn].get(name)
    if al is None: # create initial list of axis name for this named plot
        al = [_DEF_NAMES[dirn]]
        _AXES_NAMES[dirn][name] = al

    if n not in al:
        if rename:
            _plot_renameactiveaxis[dirn](name, n) # use default/selected axis
            al[0] = n
            rename = False
        else:
            _plot_createaxis(name, n, s)
            al.append(n)
    return rename, n

def _clear_axis(name):
    for dirn in ['x', 'y']:
        al = _AXES_NAMES[dirn].get(name)
        if al:
            al[0] = _DEF_NAMES[dirn]
            for n in al[1:]:
                al.remove(n)

def _process_line(x, y, title, name, mode):
    name, t, xl, yl = _parselinearg(x, y, title, name)

    if mode is None:
        _plot_clear(name)
        _clear_axis(name)

    if xl is not None:
        ax = _setup_axes(xl, 'x', name)
    else:
        ax = None
    ay = _setup_axes(yl, 'y', name)

    # generate list of axes
    xs = []
    ys = []
    for i in range(len(yl)):
        if xl is not None:
            xi = xl[0] if len(xl) == 1 else xl[i]
            if type(xi) is _types.DictType: # has axis name
                _, xi = xi.items()[0]
            if len(xl) == 1:
                if i == 0:
                    xs.append(xi)
            else:
                xs.append(xi)

        yi = yl[i]
        if type(yi) is _types.DictType: # has axis name
            _, yi = yi.items()[0]
        ys.append(yi)

    for a in xs: # if all None then make it None
        if a is not None:
            break
    else:
        xs = None

    if mode is None:
        _plot_line(name, t, xs, ys, ax, ay)
    else:
        _plot_addline(name, t, xs, ys, ax, ay)

def line(x, y=None, title=None, name=None):
    '''Plot y dataset (or list of datasets), optionally against any
    given x dataset in the named view

    Arguments:
    x -- optional dataset or list of datasets for x values
    y -- dataset or list of datasets
    title -- title of plot
    name -- name of plot view to use (if None, use default name)

    For example,
    >>> import scisoftpy as dnp
    >>> a = dnp.arange(1,10.)
    >>> b = dnp.arange(3,14.)
    >>> dnp.plot.line([a,a+12.3]) # plots two lines against array index
    >>> dnp.plot.line(2*a, [a,a+12.3]) # plots two lines against 2*a
    >>> dnp.plot.line([2*a, 3.5*b], [a,b]) # plots two lines against defined x values

    To plot with alternative axes, x and y can be single-item dictionaries or lists of
    dictionaries. Each dictionary pairs an axis as a key with the value being a dataset.
    The axis key can be a string which is used as an axis name or a tuple of name and
    position. The position is a string with recognised values: "bottom" (default) and
    "top", "left" (default) and "right" for horizontal and vertical axes, respectively.

    For example,
    >>> rads = dnp.linspace(0, dnp.pi, 21)
    >>> degs = dnp.linspace(0, 180, 31)
    >>> ysin = dnp.sin(rads)
    >>> ycos = dnp.cos(dnp.radians(degs))
    >>> dnp.plot.line([rads, {"degrees":degs}], [ysin, {("cos","right"):ycos}])

    '''
    if name is None:
        name = _PVNAME
    _process_line(x, y, title, name, None)

def addline(x, y=None, title=None, name=None):
    '''Add line(s) to existing plot, optionally against
    any given x dataset in the named view

    Arguments:
    x -- optional dataset or list of datasets for x values
    y -- dataset or list of datasets
    title -- title of plot
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    _process_line(x, y, title, name, 'add')

def updateline(x, y=None, title=None, name=None):
    '''Update existing plot by changing displayed y dataset (or list of datasets), optionally against
    any given x dataset in the named view

    Arguments:
    x -- optional dataset or list of datasets for x values
    y -- dataset or list of datasets
    title -- title of plot
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    n, t, xl, yl = _parselinearg(x, y, title, name)
    _plot_updateline(n, t, xl, yl, None, None)

plot = line
updateplot = updateline

def image(im, x=None, y=None, name=None):
    '''Plot a 2D dataset as an image in the named view with optional x and y axes

    Arguments:
    im -- image dataset
    x -- optional dataset for x-axis
    y -- optional dataset for y-axis
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if x is None:
        y = None
    if y is None:
        x = None

    _plot_image(name, x, y, im)

def images(im, x=None, y=None, name=None):
    '''Plot 2D datasets as an image in the named view with optional x and y axes

    Arguments:
    im -- image datasets (one or more)
    x -- optional dataset for x-axis
    y -- optional dataset for y-axis
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if x is None:
        y = None
    if y is None:
        x = None

    _plot_images(name, x, y, _toList(im))

def surface(s, x=None, y=None, name=None):
    '''Plot the 2D dataset as a surface in the named view with optional x and y axes

    Arguments:
    s -- surface (height field) dataset
    x -- optional dataset for x-axis
    y -- optional dataset for y-axis
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if x is None:
        y = None
    if y is None:
        x = None

    _plot_surface(name, x, y, s)

def stack(x, y=None, z=None, name=None):
    '''Plot all of the given 1D y datasets against corresponding x as a 3D stack
    with optional z coordinates in the named view

    Arguments:
    x -- optional dataset or list of datasets for x-axis
    y -- dataset or list of datasets
    z -- optional dataset for z-axis
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if not y:
        y = _toList(x)
        l = 0
        for d in y:
            if d.size > l:
                l = d.size
        x = [ _core.arange(l) ]

    _plot_stack(name, _toList(x), _toList(y), z)

def updatestack(x, y=None, z=None, name=None):
    '''Update existing 3D line stack by changing displayed y dataset (or list of datasets),
    optionally against any given x dataset with optional z coordinates in the named view

    Arguments:
    x -- optional dataset or list of datasets for x-axis
    y -- dataset or list of datasets
    z -- optional dataset for z-axis
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if not y:
        y = _toList(x)
        l = 0
        for d in y:
            if d.size > l:
                l = d.size
        x = [ _core.arange(l) ]

    _plot_updatestack(name, _toList(x), _toList(y), z)

def points(x, y=None, z=None, size=0, name=None):
    '''Plot points with given coordinates. If y is missing then x must contain
    a dataset of coordinate pairs or a list of such datasets

    Arguments:
    x -- dataset of x coords or coord pairs
    y -- optional dataset of y coords
    z -- optional dataset of z coords
    size -- integer size or dataset of sizes
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    size = _core.asarray(size)
    if z is None:
        if y is None:
            _plot_points2d(name, _toList(x), size)
        else:
            _plot_points2d(name, x, y, size)
    else:
        _plot_points3d(name, x, y, z, size)

def addpoints(x, y, z=None, size=0, name=None):
    '''Update existing plot by adding points of given coordinates

    Arguments:
    x -- dataset of x coords
    y -- dataset of y coords
    z -- optional dataset of z coords
    size -- integer size or dataset of sizes
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    size = _core.asarray(size)
    if z is None:
        _plot_updatepoints2d(name, x, y, size)
    else:
        _plot_updatepoints3d(name, x, y, z, size)


_IMAGEEXPNAME = "ImageExplorer View"

def scanforimages(path, order="none", prefix=None, suffices=None, columns=-1, rowMajor=True, name=_IMAGEEXPNAME):
    '''Scan for images in path and load into given image explorer view

    order can be "none", "alpha", "chrono"
    prefix is the start of a regular expression to match the beginnings of filenames
    suffices can be a list of filename endings (eg. ["png", "tif"], each can be a regex)
    columns is the number of columns to use in grid (-1 makes grid square)
    rowMajor determines whether images are laid out row-wise or column-wise
    
    returns number of images loaded
    '''
    maxint = ((1<<30) - 1) + (1<<30) # maximum value for signed 32-bit integer
    return _plot_scanforimages(name, path, _order(order), prefix, suffices, columns, rowMajor, maxint, 1)


def getbean(name=None):
    '''Get GUI bean (contains information from named view)

    Arguments:
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    return _plot_getbean(name)

def setbean(bean, name=None):
    '''Set GUI bean

    Arguments:
    bean -- GUI bean
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is not None:
        _plot_setbean(name, bean)

def getdatabean(name=None):
    '''Get data bean (contains data from named view)

    Arguments:
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    return _plot_getdatabean(name)

def setdatabean(bean, name=None):
    '''Set data bean

    Arguments:
    bean -- data bean
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is not None:
        _plot_setdatabean(name, bean)

def getroi(bean=None, roi=None, name=None):
    '''Get region of interest from bean

    Arguments:
    bean -- GUI bean (if None, retrieve from plot view of given name)
    roi  -- class of ROI to retrieve. If None, then get anyway
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is None:
        bean = getbean(name)
    if not parameters.roi in bean:
        return None
    r = bean[parameters.roi]
    if roi is None:
        return r
    if r is None or not isinstance(r, roi):
        return None
    return r

def setroi(bean, roi=None, send=False, name=None):
    '''Set region of interest in bean

    Arguments:
    bean -- GUI bean (if None, retrieve from and update to plot view of given name)
    roi  -- ROI to set
    send -- flag to update plot
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if roi is None:
        roi = bean
        send = True
        bean = getbean(name)
    if isinstance(bean, _guibean):
        bean[parameters.roi] = roi
    if send:
        setbean(bean, name)
    return bean

def delroi(bean=None, roi=None, send=False, name=None):
    '''Delete region of interest from bean

    Arguments:
    bean -- GUI bean (if None, retrieve from and update to plot view of given name)
    roi  -- class of ROI to remove. If None, then remove anyway
    send -- flag to update plot
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is None:
        send = True
        bean = getbean(name)
        
    if parameters.roi in bean:
        if roi is None or isinstance(bean[parameters.roi], roi):
            bean[parameters.roi] = None

    if send:
        setbean(bean, name)
    return bean

from scisoftpy.dictutils import ListDict

class roi_list(ListDict):
    def __init__(self, data=None):
        super(roi_list, self).__init__(data=data, warn=False, lock=False, interactive=False)

def getrois(bean=None, roi=None, name=None):
    '''Get list/dict of regions of interest from bean

    Arguments:
    bean -- GUI bean (if None, retrieve from plot view of given name)
    roi  -- class of ROI to retrieve. If None, then get anyway
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is None:
        bean = getbean(name)
    if not parameters.roilist in bean:
        return None
    rs = bean[parameters.roilist]
    if rs is None or len(rs) == 0:
        return None
    try:
        iter(rs)
    except:
        rs = [rs]
    if roi is None:
        rl = [(r.name, r) for r in rs]
    else:
        rl = [(r.name, r) for r in rs if isinstance(r, roi)]
    return roi_list(rl)

def setrois(bean, roilist=None, send=False, name=None):
    '''Set list/dict of regions of interest in bean
    Arguments:
    bean    -- GUI bean (if None, retrieve from and update to plot view of given name)
    roilist -- ROI list to set
    send    -- flag to update plot
    name    -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if roilist is None:
        roilist = bean
        send = True
        bean = getbean(name)

    if not isinstance(roilist, (roi.point_list, roi.line_list, roi.rectangle_list, roi.sector_list, roi.ellipse_list, roi.circle_list)):
        r = roilist[0]
        if isinstance(r, roi.point):
            rtype = roi.point
            nlist = roi.point_list()
        elif isinstance(r, roi.line):
            rtype = roi.line
            nlist = roi.line_list()
        elif isinstance(r, roi.rectangle):
            rtype = roi.rectangle
            nlist = roi.rectangle_list()
        elif isinstance(r, roi.sector):
            rtype = roi.sector
            nlist = roi.sector_list()
        elif isinstance(r, roi.ellipse):
            rtype = roi.ellipse
            nlist = roi.ellipse_list()
        elif isinstance(r, roi.circle):
            rtype = roi.circle
            nlist = roi.circle_list()
        else:
            raise TypeError, "Type of first item not supported"

        if isinstance(roilist, roi_list):
            for k in roilist:
                r = roilist[k]
                if isinstance(r, rtype):
                    nlist.append(r)
        else:
            for r in roilist:
                if isinstance(r, rtype):
                    nlist.append(r)
        roilist = nlist
    bean[parameters.roilist] = roilist
    if send:
        setbean(bean, name)
    return bean

def delrois(bean=None, roi=None, send=False, name=None):
    '''Delete list/dict of regions of interest from bean

    Arguments:
    bean -- GUI bean (if None, retrieve from and update to plot view of given name)
    roi  -- class of ROI or ROI list to remove. If None, then remove anyway
    send -- flag to update plot
    name -- name of plot view to use (if None, use default name)
    '''
    if name is None:
        name = _PVNAME
    if bean is None:
        send = True
        bean = getbean(name)

    if parameters.roilist in bean:
        rl = bean[parameters.roilist]
        if roi is None or isinstance(rl, roi) or isinstance(rl[0], roi):
            bean[parameters.roilist] = None
    if send:
        setbean(bean, name)
    return bean

def getline(bean=None, name=None):
    '''Get linear region of interest'''
    if name is None:
        name = _PVNAME
    return getroi(bean, roi=roi.line, name=name)

def getlines(bean=None, name=None):
    '''Get list of linear regions of interest'''
    if name is None:
        name = _PVNAME
    return getrois(bean, roi=roi.line, name=name)

def getrect(bean=None, name=None):
    '''Get rectangular region of interest'''
    if name is None:
        name = _PVNAME
    return getroi(bean, roi=roi.rectangle, name=name)

def getrects(bean=None, name=None):
    '''Get list of rectangular regions of interest'''
    if name is None:
        name = _PVNAME
    return getrois(bean, roi=roi.rectangle, name=name)

def getsect(bean=None, name=None):
    '''Get sector region of interest'''
    if name is None:
        name = _PVNAME
    return getroi(bean, roi=roi.sector, name=name)

def getsects(bean=None, name=None):
    '''Get list of sector regions of interest'''
    if name is None:
        name = _PVNAME
    return getrois(bean, roi=roi.sector, name=name)


def getfiles(bean):
    '''Get list of selected files'''
    try:
        fn = bean[parameters.fileselect]
    except KeyError:
        print "No selection has been made and sent to server"
        return None
    if fn is None:
        print "No selection has been made and sent to server"
        return None
    fl = []
    for f in fn:
        fl.append(f)
    fl.sort()
    return fl

_H5TVNAME="hdf5TreeViewer"
def viewnexus(tree, name=_H5TVNAME):
    '''View a NeXus/HDF5 tree in the named view'''
    _plot_viewnexustree(name, tree)
