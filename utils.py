import cv2
import numpy
import scipy.interpolate

def createCurveFunc(points): # Crear una función de curva a partir de puntos dados
    if points is None or len(points) < 2: # 
        return None # Si no hay suficientes puntos, devolver None
    xs, ys = zip(*points) # Separar puntos en coordenadas x e y
    kind = 'linear' if len(points) < 4 else 'cubic' # Elegir tipo de interpolación
    return scipy.interpolate.interp1d(xs, ys, kind, bounds_error=False) # Crear y devolver la función de interpolación

def createLookupArray(func, length=256): # Crear un arreglo de búsqueda a partir de una función dada
    if func is None: # Si la función es None
        return None # Devolver None
    lookupArray = numpy.empty(length) # Crear un arreglo vacío
    for i in range(length): # Rellenar el arreglo con valores de la función
        func_i = func(i) # Evaluar la función en i
        lookupArray[i] = numpy.clip(func_i, 0, length - 1) # Asegurarse de que el valor esté dentro de los límites
    return lookupArray # Devolver el arreglo de búsqueda

def applyLookupArray(lookupArray, src, dst): # Aplicar un arreglo de búsqueda a una imagen fuente para obtener una imagen destino
    if lookupArray is None: # Si el arreglo de búsqueda es None
        return # No hacer nada
    dst[:] = lookupArray[src] # Aplicar el arreglo de búsqueda

def createCompositeFunc(func0, func1): # Crear una función compuesta a partir de dos funciones dadas
    if func0 is None: # Si la primera función es None
        return func1 # Devolver la segunda función
    if func1 is None: # Si la segunda función es None
        return func0 # Devolver la primera función
    return lambda x: func0(func1(x)) # Devolver la función compuesta

def createFlatView(array): # Crear una vista plana de un arreglo numpy
    flatView = array.view() # Crear una vista del arreglo
    flatView.shape = array.size # Cambiar la forma a una dimensión
    return flatView # Devolver la vista plana