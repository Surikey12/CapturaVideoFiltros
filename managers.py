import cv2
import numpy
import time

class CaptureManager(object): # Clase para gestionar la captura de video
    def __init__(self, capture, previewWindowManager=None, shouldMirrorPreview=False): # Inicializador de la clase CaptureManager
        self.previewWindowManager = previewWindowManager # Ventana de previsualización
        self.shouldMirrorPreview = shouldMirrorPreview # Indica si se debe espejar la previsualización
        self._capture = capture # Objeto de captura de video
        self._channel = 0 # Canal de captura (0 por defecto)
        self._enteredFrame = False # Indica si se ha entrado en un frame
        self._frame = None # Frame actual
        self._imageFilename = None # Nombre del archivo para guardar imagen
        self._videoFilename = None # Nombre del archivo para guardar video
        self._videoEncoding = None # Codificación de video
        self._videoWriter = None # Objeto de escritura de video
        self._startTime = None  # Tiempo de inicio de la captura
        self._framesElapsed = 0 # Número de frames capturados
        self._fpsEstimate = None # Estimación de FPS

    # Getter y setter para el canal de captura
    @property 
    def channel(self):
        return self._channel # Obtener el canal de captura

    @channel.setter 
    def channel(self, value):
        if self._channel != value: # Si el canal ha cambiado
            self._channel = value # Actualizar el canal
            self._frame = None # Resetear el frame actual

    @property 
    def frame(self): 
        if self._enteredFrame and self._frame is None: # Si se ha entrado en un frame y no hay frame actual
            _, self._frame = self._capture.retrieve() # Recuperar el frame
        return self._frame # Devolver el frame actual

    def enterFrame(self): # Entrar en un nuevo frame
        assert not self._enteredFrame # Asegurarse de que no se ha entrado ya en un frame
        if self._capture is not None: # Si el objeto de captura no es None
            self._enteredFrame = self._capture.grab() # Capturar un nuevo frame

    def exitFrame(self): # Salir del frame actual
        if self.frame is None: # Si no hay frame actual
            self._enteredFrame = False # Salir del frame sin hacer nada más
            return
        if self._framesElapsed == 0: # Si es el primer frame
            self._startTime = time.time()  # Registrar el tiempo de inicio
        else: # Calcular la estimación de FPS
            timeElapsed = time.time() - self._startTime # Tiempo transcurrido
            self._fpsEstimate = self._framesElapsed / timeElapsed # Estimación de FPS
        self._framesElapsed += 1 # Incrementar el contador de frames

        if self.previewWindowManager is not None: # Si hay una ventana de previsualización
            if self.shouldMirrorPreview: # Si se debe espejar la previsualización
                mirroredFrame = numpy.fliplr(self._frame).copy() # Espejar el frame
                self.previewWindowManager.show(mirroredFrame) # Mostrar el frame espejado
            else: # Si no se debe espejar la previsualización
                self.previewWindowManager.show(self._frame) # Mostrar el frame normal

        if self._imageFilename: # Si hay un nombre de archivo para guardar imagen
            cv2.imwrite(self._imageFilename, self._frame) # Guardar la imagen
            self._imageFilename = None # Resetear el nombre del archivo

        if self._videoFilename: # Si hay un nombre de archivo para guardar video
            self._writeVideoFrame() # Escribir el frame en el video

        self._frame = None # Resetear el frame actual
        self._enteredFrame = False # Salir del frame

    def writeImage(self, filename): # Guardar la imagen actual en un archivo
        self._imageFilename = filename # Establecer el nombre del archivo

    def startWritingVideo(self, filename, encoding=cv2.VideoWriter_fourcc('I', '4', '2', '0')): # Iniciar la grabación de video
        self._videoFilename = filename # Establecer el nombre del archivo
        self._videoEncoding = encoding # Establecer la codificación de video

    def stopWritingVideo(self): # Detener la grabación de video
        self._videoFilename = None # Resetear el nombre del archivo
        self._videoEncoding = None # Resetear la codificación de video
        self._videoWriter = None # Resetear el objeto de escritura de video

    def _writeVideoFrame(self): # Escribir el frame actual en el archivo de video
        if not self._videoFilename: # Si no hay nombre de archivo,
            return
        if self._videoWriter is None: # Si el objeto de escritura de video no está inicializado
            fps = self._capture.get(cv2.CAP_PROP_FPS) # Obtener los FPS del objeto de captura
            if fps == 0.0: # Si no se pueden obtener los FPS
                if self._framesElapsed < 20: # Si hay pocos frames capturados
                    return # No hacer nada
                fps = self._fpsEstimate # Usar la estimación de FPS
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)), # Obteniendo el ancho del frame
                    int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))) # Obteniendo el alto del frame
             # Crear el objeto de escritura de video
            self._videoWriter = cv2.VideoWriter(
                self._videoFilename, self._videoEncoding, fps, size)
        self._videoWriter.write(self._frame) # Escribir el frame en el archivo de video

class WindowManager(object): # Clase para gestionar la ventana de visualización
    def __init__(self, windowName, keypressCallback=None): # Inicializador de la clase WindowManager
        self.keypressCallback = keypressCallback # Callback para manejar pulsaciones de teclas
        self._windowName = windowName # Nombre de la ventana
        self._isWindowCreated = False # Indica si la ventana ha sido creada

    # Getter para el estado de la ventana
    @property
    def isWindowCreated(self):
        return self._isWindowCreated # Devolver el estado de la ventana

    def createWindow(self): # Crear la ventana de visualización con OpenCV
        cv2.namedWindow(self._windowName) 
        self._isWindowCreated = True # Indicar que la ventana ha sido creada

    def show(self, frame): # Mostrar un frame en la ventana
        cv2.imshow(self._windowName, frame)

    def destroyWindow(self): # Destruir la ventana de visualización
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False # Indicar que la ventana ha sido destruida

    def processEvents(self): # Procesar eventos de la ventana
        keycode = cv2.waitKey(1) # Esperar 1 ms por una pulsación de tecla
        if self.keypressCallback and keycode != -1: # Si hay un callback y se ha presionado una tecla
            keycode &= 0xFF # Normalizar el keycode
            self.keypressCallback(keycode) # Llamar al callback con el keycode
