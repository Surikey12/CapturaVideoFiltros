import cv2
import numpy
import scipy.interpolate

def createCurveFunc(points):
    if points is None or len(points) < 2:
        return None
    xs, ys = zip(*points)
    kind = 'linear' if len(points) < 4 else 'cubic'
    return scipy.interpolate.interp1d(xs, ys, kind, bounds_error=False)

def createLookupArray(func, length=256):
    if func is None:
        return None
    lookupArray = numpy.empty(length)
    for i in range(length):
        func_i = func(i)
        lookupArray[i] = numpy.clip(func_i, 0, length - 1)
    return lookupArray

def applyLookupArray(lookupArray, src, dst):
    if lookupArray is None:
        return
    dst[:] = lookupArray[src]

def createCompositeFunc(func0, func1):
    if func0 is None:
        return func1
    if func1 is None:
        return func0
    return lambda x: func0(func1(x))

def createFlatView(array):
    flatView = array.view()
    flatView.shape = array.size
    return flatView