import cv2
import filters
from managers import WindowManager, CaptureManager

class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager('Cameo', self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture(0), self._windowManager, True)
        self._curveFilter = filters.BGRPortraCurveFilter()

    def run(self):
        """Run the main loop."""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame
            # Aplicar filtro de detección de bordes y filtro de curvas
            filters.strokeEdges(frame, frame)
            self._curveFilter.apply(frame, frame)

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
            self._curveFilter = filters.BGRPortraCurveFilter()
        elif keycode == ord('2'):
            self._curveFilter = filters.BGRProviaCurveFilter()
        elif keycode == ord('3'):
            self._curveFilter = filters.BGRVelviaCurveFilter()
        elif keycode == ord('4'):
            self._curveFilter = filters.BGRCrossProcessCurveFilter()


if __name__ == "__main__":
    Cameo().run()
