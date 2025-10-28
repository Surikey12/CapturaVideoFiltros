readme_content = """
# Cameo - Aplicación de Filtros con OpenCV

Este proyecto implementa una aplicación interactiva de captura de video en tiempo real usando OpenCV, con la capacidad de aplicar múltiples filtros visuales mediante el teclado.
Este proyecto está basado en el libro OpenCV Computer Vision Projects with Python de Joseph Howse, Prateek Joshi y Michael Beyeler.

## Archivos

- `managers.py`: Define las clases `CaptureManager` y `WindowManager` para manejar la captura de video, la visualización en ventana y la escritura de imágenes y video.
- `filters.py`: Contiene funciones y clases para aplicar filtros de color, curvas, bordes y convolución.
- `utils.py`: Proporciona funciones auxiliares para interpolación de curvas, creación de arrays de búsqueda y composición de funciones.
- `cameo.py`: Archivo principal que ejecuta la aplicación, captura video desde la cámara y permite aplicar filtros mediante teclas.

## Controles por teclado 

- 1: Filtro Portra
- 2: Filtro Provia
- 3: Filtro Velvia
- 4: Filtro CrossProcess
- 5: Filtro Sharpen
- 6: Filtro Emboss
- 7: Filtro Blur
- 8: Filtro FindEdges
- 9: Filtro recolorRC
- 0: Filtro recolorRGV
- q: Filtro recolorCMV
- espacio: Captura imagen (se guarda como screenshot.png)
- tab: Inicia/detiene grabación de video (se guarda como screencast.avi)
- esc: Cierra la aplicación

## Instalación 

1. Instala las dependencias necesarias:
```bash
pip install opencv-python numpy scipy

