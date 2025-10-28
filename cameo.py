import cv2
import filters
from managers import WindowManager, CaptureManager

class Cameo(object): # Clase principal de la aplicación Cameo
    def __init__(self): # Inicializador de la clase Cameo
        self._windowManager = WindowManager('Cameo', self.onKeypress) # Ventana principal
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, True) # Captura de video
        self._activeFilter = 'portra'  # Filtro inicial

        # Diccionario de filtros disponibles
        self._filterMap = {
            'portra': filters.BGRPortraCurveFilter(), # Filtro Portra
            'provia': filters.BGRProviaCurveFilter(), # Filtro Provia
            'velvia': filters.BGRVelviaCurveFilter(), # Filtro Velvia
            'cross': filters.BGRCrossProcessCurveFilter(), # Filtro Cross Process
            'sharpen': filters.SharpenFilter(), # Filtro de nitidez
            'emboss': filters.EmbossFilter(), # Filtro de relieve
            'blur': filters.BlurFilter(), # Filtro de desenfoque
            'edges': filters.FindEdgesFilter(), # Filtro de detección de bordes
            'rc': filters.recolorRC, # Filtro de recoloración RC
            'rgv': filters.recolorRGV, # Filtro de recoloración RGV
            'cmv': filters.recolorCMV # Filtro de recoloración CMV
        }

    def run(self): #Función para ejecutar la aplicación
        """Run the main loop."""
        self._windowManager.createWindow() # Crear la ventana principal
        while self._windowManager.isWindowCreated: # Bucle principal mientras la ventana esté abierta
            self._captureManager.enterFrame() # Capturar un nuevo frame
            frame = self._captureManager.frame # Obtener el frame capturado
            
            # Aplicar filtro de bordes al frame
            filters.strokeEdges(frame, frame) 

            # Aplicar el filtro activo
            filterObj = self._filterMap.get(self._activeFilter)
            if callable(filterObj):  # Si es función como recolorRC es decir, que se puede llamar directamente
                filterObj(frame, frame)
            else:  # Si es clase con método apply, es decir, que necesita instanciarse
                filterObj.apply(frame, frame)


            self._captureManager.exitFrame() # Procesar el frame capturado
            self._windowManager.processEvents() # Procesar eventos de la ventana

    def onKeypress(self, keycode):
        """Manejar una pulsación de tecla.
           space: take a screenshot
           tab: start/stop recording a screencast
           sc: quit the program
        """
        if keycode == 32:  # al prescionar la tecla espacio: tomar captura de pantalla
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9:  # al prescionar la tecla tab: grabar video
            if not self._captureManager._videoWriter: # Si no se está grabando, iniciar grabación
                self._captureManager.startWritingVideo('screencast.avi')
            else: # Si se está grabando, detener grabación
                self._captureManager.stopWritingVideo()
        elif keycode == 27:  # al prescionar la tecla esc: salir del programa
            self._windowManager.destroyWindow()     
        # Cambiar el filtro activo según la tecla presionada desde 1 hasta 0 y q
        elif keycode == ord('1'): 
            self._activeFilter = 'portra'
        elif keycode == ord('2'): 
            self._activeFilter = 'provia'
        elif keycode == ord('3'):
            self._activeFilter = 'velvia'
        elif keycode == ord('4'):
            self._activeFilter = 'cross'
        elif keycode == ord('5'):
            self._activeFilter = 'sharpen'
        elif keycode == ord('6'):
            self._activeFilter = 'emboss'
        elif keycode == ord('7'):
            self._activeFilter = 'blur'
        elif keycode == ord('8'):
            self._activeFilter = 'edges'
        elif keycode == ord('9'):
           self._activeFilter = 'rc'
        elif keycode == ord('0'):
            self._activeFilter = 'rgv'
        elif keycode == ord('q'):
            self._activeFilter = 'cmv'

        print(f"Filtro activo: {self._activeFilter}") # Imprimir el filtro activo en la consola

# Punto de entrada del programa
if __name__ == "__main__":
    Cameo().run()
