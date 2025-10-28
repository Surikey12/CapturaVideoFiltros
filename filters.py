import cv2
import numpy
import utils

# --- Filtros de color ---
def recolorRC(src, dst):
    b, g, r = cv2.split(src)
    cv2.addWeighted(b, 0.5, g, 0.5, 0, b)
    cv2.merge((b, b, r), dst)

def recolorRGV(src, dst):
    b, g, r = cv2.split(src)
    cv2.min(b, g, b)
    cv2.min(b, r, b)
    cv2.merge((b, g, r), dst)

def recolorCMV(src, dst):
    b, g, r = cv2.split(src)
    cv2.max(b, g, b)
    cv2.max(b, r, b)
    cv2.merge((b, g, r), dst)

# --- Filtro de bordes ---
def strokeEdges(src, dst, blurKsize=7, edgeKsize=5):
    if blurKsize >= 3:
        blurredSrc = cv2.medianBlur(src, blurKsize)
        graySrc = cv2.cvtColor(blurredSrc, cv2.COLOR_BGR2GRAY)
    else:
        graySrc = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    cv2.Laplacian(graySrc, cv2.CV_8U, graySrc, ksize=edgeKsize)
    normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc)
    channels = cv2.split(src)
    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha
    cv2.merge(channels, dst)

# --- Filtros de convolución ---
class VConvolutionFilter(object):
    def __init__(self, kernel):
        self._kernel = kernel
    def apply(self, src, dst):
        cv2.filter2D(src, -1, self._kernel, dst)

class SharpenFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
        super().__init__(kernel)

class FindEdgesFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
        super().__init__(kernel)

class BlurFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.ones((5,5), numpy.float32) / 25
        super().__init__(kernel)

class EmbossFilter(VConvolutionFilter):
    def __init__(self):
        kernel = numpy.array([[-2,-1,0],[-1,1,1],[0,1,2]])
        super().__init__(kernel)

# --- Filtros de curvas ---
class VFuncFilter(object):
    def __init__(self, vFunc=None, dtype=numpy.uint8):
        length = numpy.iinfo(dtype).max + 1
        self._vLookupArray = utils.createLookupArray(vFunc, length)
    def apply(self, src, dst):
        srcFlatView = utils.createFlatView(src)
        dstFlatView = utils.createFlatView(dst)
        utils.applyLookupArray(self._vLookupArray, srcFlatView, dstFlatView)

class VCurveFilter(VFuncFilter):
    def __init__(self, vPoints, dtype=numpy.uint8):
        super().__init__(utils.createCurveFunc(vPoints), dtype)

class BGRFuncFilter(object):
    def __init__(self, vFunc=None, bFunc=None, gFunc=None, rFunc=None, dtype=numpy.uint8):
        length = numpy.iinfo(dtype).max + 1
        self._bLookupArray = utils.createLookupArray(utils.createCompositeFunc(bFunc, vFunc), length)
        self._gLookupArray = utils.createLookupArray(utils.createCompositeFunc(gFunc, vFunc), length)
        self._rLookupArray = utils.createLookupArray(utils.createCompositeFunc(rFunc, vFunc), length)
    def apply(self, src, dst):
        b, g, r = cv2.split(src)
        utils.applyLookupArray(self._bLookupArray, b, b)
        utils.applyLookupArray(self._gLookupArray, g, g)
        utils.applyLookupArray(self._rLookupArray, r, r)
        cv2.merge([b, g, r], dst)

class BGRCurveFilter(BGRFuncFilter):
    def __init__(self, vPoints=None, bPoints=None, gPoints=None, rPoints=None, dtype=numpy.uint8):
        super().__init__(utils.createCurveFunc(vPoints), utils.createCurveFunc(bPoints),
                         utils.createCurveFunc(gPoints), utils.createCurveFunc(rPoints), dtype)

# --- Filtros de curvas predefinidos ---
class BGRPortraCurveFilter(BGRCurveFilter):
    def __init__(self, dtype=numpy.uint8):
        super().__init__(
            vPoints=[(0,0),(23,20),(157,173),(255,255)],
            bPoints=[(0,0),(41,46),(231,228),(255,255)],
            gPoints=[(0,0),(52,47),(189,196),(255,255)],
            rPoints=[(0,0),(69,69),(213,218),(255,255)],
            dtype=dtype)

class BGRProviaCurveFilter(BGRCurveFilter):
    def __init__(self, dtype=numpy.uint8):
        super().__init__(
            bPoints=[(0,0),(35,25),(205,227),(255,255)],
            gPoints=[(0,0),(27,21),(196,207),(255,255)],
            rPoints=[(0,0),(59,54),(202,210),(255,255)],
            dtype=dtype)

class BGRVelviaCurveFilter(BGRCurveFilter):
    def __init__(self, dtype=numpy.uint8):
        super().__init__(
            vPoints=[(0,0),(128,118),(221,215),(255,255)],
            bPoints=[(0,0),(25,21),(122,153),(165,206),(255,255)],
            gPoints=[(0,0),(25,21),(95,102),(181,208),(255,255)],
            rPoints=[(0,0),(41,28),(183,209),(255,255)],
            dtype=dtype)

class BGRCrossProcessCurveFilter(BGRCurveFilter):
    def __init__(self, dtype=numpy.uint8):
        super().__init__(
            bPoints=[(0,20),(255,235)],
            gPoints=[(0,0),(56,39),(208,226),(255,255)],
            rPoints=[(0,0),(56,22),(211,255),(255,255)],
            dtype=dtype)