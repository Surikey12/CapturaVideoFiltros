import cv2
import numpy
import utils

# --- Filtros de color ---
def recolorRC(src, dst): # Recoloración RC
    b, g, r = cv2.split(src) # Separar canales
    cv2.addWeighted(b, 0.5, g, 0.5, 0, b)  # Mezclar azul y verde
    cv2.merge((b, b, r), dst) # Combinar canales

def recolorRGV(src, dst): # Recoloración RGV
    b, g, r = cv2.split(src) # Separar canales
    cv2.min(b, g, b) # Mínimo entre azul y verde
    cv2.min(b, r, b) # Mínimo entre azul y rojo
    cv2.merge((b, g, r), dst) # Combinar canales

def recolorCMV(src, dst): # Recoloración CMV
    b, g, r = cv2.split(src) # Separar canales
    cv2.max(b, g, b) # Máximo entre azul y verde
    cv2.max(b, r, b) # Máximo entre azul y rojo
    cv2.merge((b, g, r), dst) # Combinar canales

# --- Filtro de bordes ---
def strokeEdges(src, dst, blurKsize=7, edgeKsize=5): # Resaltar bordes
    if blurKsize >= 3: # Si el tamaño del kernel de desenfoque es mayor o igual a 3
        blurredSrc = cv2.medianBlur(src, blurKsize) # Aplicar desenfoque
        graySrc = cv2.cvtColor(blurredSrc, cv2.COLOR_BGR2GRAY) # Convertir a escala de grises
    else: # Si no
        graySrc = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) # Convertir a escala de grises
    cv2.Laplacian(graySrc, cv2.CV_8U, graySrc, ksize=edgeKsize) # Aplicar filtro Laplaciano
    normalizedInverseAlpha = (1.0 / 255) * (255 - graySrc) # Normalizar e invertir
    channels = cv2.split(src) # Separar canales
    for channel in channels: # Aplicar efecto de borde a cada canal
        channel[:] = channel * normalizedInverseAlpha # Multiplicar canal por el efecto
    cv2.merge(channels, dst) # Combinar canales

# --- Filtros de convolución ---
class VConvolutionFilter(object): # Filtro de convolución genérico
    def __init__(self, kernel): # Inicializador con el kernel de convolución
        self._kernel = kernel # Guardar el kernel
    def apply(self, src, dst): # Aplicar el filtro
        cv2.filter2D(src, -1, self._kernel, dst) # Aplicar convolución

class SharpenFilter(VConvolutionFilter): # Filtro de nitidez
    def __init__(self): # Inicializador
        kernel = numpy.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]) # Kernel de nitidez con valor 9 en el centro
        super().__init__(kernel) # Llamar al inicializador de la clase base

class FindEdgesFilter(VConvolutionFilter): # Filtro de detección de bordes
    def __init__(self): # Inicializador
        kernel = numpy.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]) # Kernel de detección de bordes con valor 8 en el centro
        super().__init__(kernel) # Llamar al inicializador de la clase base

class BlurFilter(VConvolutionFilter): # Filtro de desenfoque
    def __init__(self): # Inicializador
        kernel = numpy.ones((5,5), numpy.float32) / 25 # Kernel de desenfoque 5x5
        super().__init__(kernel) # Llamar al inicializador de la clase base

class EmbossFilter(VConvolutionFilter): # Filtro de relieve
    def __init__(self): # Inicializador
        kernel = numpy.array([[-2,-1,0],[-1,1,1],[0,1,2]]) # Kernel de relieve con valores que resaltan bordes
        super().__init__(kernel) # Llamar al inicializador de la clase base 

# --- Filtros de curvas ---
class VFuncFilter(object): # Filtro basado en función de valor
    def __init__(self, vFunc=None, dtype=numpy.uint8): # Inicializador con función y tipo de dato
        length = numpy.iinfo(dtype).max + 1 # Longitud del arreglo de búsqueda
        self._vLookupArray = utils.createLookupArray(vFunc, length) # Crear arreglo de búsqueda
    def apply(self, src, dst): # Aplicar el filtro
        srcFlatView = utils.createFlatView(src) # Vista plana del src
        dstFlatView = utils.createFlatView(dst) # Vista plana del dst
        utils.applyLookupArray(self._vLookupArray, srcFlatView, dstFlatView) # Aplicar el arreglo de búsqueda

class VCurveFilter(VFuncFilter): # Filtro de curva basado en puntos
    def __init__(self, vPoints, dtype=numpy.uint8): # Inicializador con puntos de la curva y tipo de dato
        super().__init__(utils.createCurveFunc(vPoints), dtype) # Llamar al inicializador de la clase base

class BGRFuncFilter(object): # Filtro basado en función para cada canal BGR
    def __init__(self, vFunc=None, bFunc=None, gFunc=None, rFunc=None, dtype=numpy.uint8): # Inicializador con funciones y tipo de dato
        length = numpy.iinfo(dtype).max + 1 # Longitud del arreglo de búsqueda
        self._bLookupArray = utils.createLookupArray(utils.createCompositeFunc(bFunc, vFunc), length) # Crear arreglo de búsqueda para azul
        self._gLookupArray = utils.createLookupArray(utils.createCompositeFunc(gFunc, vFunc), length) # Crear arreglo de búsqueda para verde
        self._rLookupArray = utils.createLookupArray(utils.createCompositeFunc(rFunc, vFunc), length) # Crear arreglo de búsqueda para rojo
    def apply(self, src, dst): # Aplicar el filtro
        b, g, r = cv2.split(src) # Separar canales
        utils.applyLookupArray(self._bLookupArray, b, b) # Aplicar arreglo de búsqueda al canal azul
        utils.applyLookupArray(self._gLookupArray, g, g) # Aplicar arreglo de búsqueda al canal verde
        utils.applyLookupArray(self._rLookupArray, r, r) # Aplicar arreglo de búsqueda al canal rojo
        cv2.merge([b, g, r], dst) # Combinar canales

class BGRCurveFilter(BGRFuncFilter): # Filtro de curva para cada canal BGR
    def __init__(self, vPoints=None, bPoints=None, gPoints=None, rPoints=None, dtype=numpy.uint8): # Inicializador con puntos de la curva y tipo de dato
        super().__init__(utils.createCurveFunc(vPoints), utils.createCurveFunc(bPoints), # Llamar al inicializador de la clase base
                         utils.createCurveFunc(gPoints), utils.createCurveFunc(rPoints), dtype) # Crear función de curva para cada canal

# --- Filtros de curvas predefinidos ---
class BGRPortraCurveFilter(BGRCurveFilter): # Filtro de curva Portra
    def __init__(self, dtype=numpy.uint8): # Inicializador
        # Llamar al inicializador de la clase base con puntos específicos para el filtro Portra
        super().__init__( 
            vPoints=[(0,0),(23,20),(157,173),(255,255)],
            bPoints=[(0,0),(41,46),(231,228),(255,255)],
            gPoints=[(0,0),(52,47),(189,196),(255,255)],
            rPoints=[(0,0),(69,69),(213,218),(255,255)],
            dtype=dtype)

class BGRProviaCurveFilter(BGRCurveFilter): # Filtro de curva Provia
    def __init__(self, dtype=numpy.uint8): # Inicializador
        # Llamar al inicializador de la clase base con puntos específicos para el filtro Provia
        super().__init__(
            bPoints=[(0,0),(35,25),(205,227),(255,255)],
            gPoints=[(0,0),(27,21),(196,207),(255,255)],
            rPoints=[(0,0),(59,54),(202,210),(255,255)],
            dtype=dtype)

class BGRVelviaCurveFilter(BGRCurveFilter): # Filtro de curva Velvia
    def __init__(self, dtype=numpy.uint8): # Inicializador
        # Llamar al inicializador de la clase base con puntos específicos para el filtro Velvia
        super().__init__(
            vPoints=[(0,0),(128,118),(221,215),(255,255)],
            bPoints=[(0,0),(25,21),(122,153),(165,206),(255,255)],
            gPoints=[(0,0),(25,21),(95,102),(181,208),(255,255)],
            rPoints=[(0,0),(41,28),(183,209),(255,255)],
            dtype=dtype)

class BGRCrossProcessCurveFilter(BGRCurveFilter): # Filtro de curva Cross Process
    def __init__(self, dtype=numpy.uint8): # Inicializador
        # Llamar al inicializador de la clase base con puntos específicos para el filtro Cross Process
        super().__init__(
            bPoints=[(0,20),(255,235)],
            gPoints=[(0,0),(56,39),(208,226),(255,255)],
            rPoints=[(0,0),(56,22),(211,255),(255,255)],
            dtype=dtype)