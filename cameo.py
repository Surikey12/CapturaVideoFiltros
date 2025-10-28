import cv2
import filters
from managers import WindowManager, CaptureManager

class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, True)
        self._activeFilter = 'portra'  # Filtro inicial

        # Diccionario de filtros disponibles
        self._filterMap = {
            'portra': filters.BGRPortraCurveFilter(),
            'provia': filters.BGRProviaCurveFilter(),
            'velvia': filters.BGRVelviaCurveFilter(),
            'cross': filters.BGRCrossProcessCurveFilter(),
            'sharpen': filters.SharpenFilter(),
            'emboss': filters.EmbossFilter(),
            'blur': filters.BlurFilter(),
            'edges': filters.FindEdgesFilter(),
            'rc': filters.recolorRC,
            'rgv': filters.recolorRGV,
            'cmv': filters.recolorCMV
        }


    def run(self):
        """Run the main loop."""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame
            
            # Aplicar bordes
            filters.strokeEdges(frame, frame)

            # Aplicar filtro activo
            filterObj = self._filterMap.get(self._activeFilter)
            if callable(filterObj):  # Si es función como recolorRC
                filterObj(frame, frame)
            else:  # Si es clase con método apply
                filterObj.apply(frame, frame)


            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self, keycode):
        """Handle a keypress.
           space: take a screenshot
           tab: start/stop recording a screencast
           sc: quit the program
        """
        if keycode == 32:  # espacio: capturar imagen
            self._captureManager.writeImage('screenshot.png')
        elif keycode == 9:  # tab: grabar video
            if not self._captureManager._videoWriter:
                self._captureManager.startWritingVideo('screencast.avi')
            else:
                self._captureManager.stopWritingVideo()
        elif keycode == 27:  # esc: salir
            self._windowManager.destroyWindow()     
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

        print(f"Filtro activo: {self._activeFilter}")


if __name__ == "__main__":
    Cameo().run()
