# Python Easy Chess GUI (Fork español y simplificado)

Una interfaz gráfica de ajedrez compacta y funcional desarrollada en Python. Esta versión ha sido simplificada drásticamente para enfocarse en la facilidad de uso, la automatización y la integración futura con hardware (LEDs/ESP32).

---

## Características Principales

- **Descarga Automática de Motor**: No se necesita buscar Stockfish. El programa detecta el sistema operativo (Windows, Linux, macOS) y arquitectura (x64, ARM/M1/M2) y descarga la versión correcta de Stockfish 16 automáticamente.
- **Interfaz Ultra-Compacta**: Desarrollada con `FreeSimpleGUI`, diseñada para ser ligera y directa.
- **Modos de Juego**:
    - **vs Jugador**: Juega localmente con otra persona.
    - **vs BOT**: Enfrenta al motor de ajedrez Stockfish.
- **Asistente de Movimientos**: Sugerencias visuales en tiempo real sobre el tablero para ayudarte a encontrar la mejor jugada. Funciona en ambos modos.
- **Gestión de FEN**: Carga cualquier posición de ajedrez pegando una cadena FEN.
- **Feedback Visual Avanzado**: Resaltado de movimientos válidos, capturas, enroques y errores.

---

## Requisitos e Instalación

### 1. Requisitos
- Python 3.8 o superior.
- Dependencias de Python:
  ```bash
  pip install python-chess FreeSimpleGUI
  ```

### 2. Instalación en Linux
Si usas Linux, asegúrate de tener instaladas las librerías de `tkinter`:
```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-tk
```

---

## Instrucciones de Uso

1. **Inicio**: Ejecuta `python play_chess.py`. En el primer inicio, el programa descargará el motor Stockfish en la carpeta `engines/`. Puede tardar unos minutos.
2. **Selección/Deselección**: Haz clic en una pieza para ver sus movimientos válidos. Haz clic de nuevo en la misma pieza para deseleccionarla.
3. **Bot y Asistente**:
    - Usa el botón **vs BOT** para cambiar entre modos y activar el motor oponente.
    - Usa el botón **ASISTENTE** para ver la mejor jugada sugerida (se resalta en el tablero).
4. **Confirmación de Acciones**: Botones como "REINICIAR" o "SALIR" requieren un doble clic de confirmación para evitar cierres accidentales.

---

## Detalles Técnicos para Desarrolladores

- **Multihilo (Threading)**: El motor Stockfish se ejecuta en hilos separados para evitar que la interfaz se congele durante el análisis.
- **Thread-Safety**: Se utiliza `board.copy()` al pasar datos al motor para asegurar que la lógica de la GUI no interfiera con el análisis.
- **Protocolo UCI**: Comunicación estándar con el motor de ajedrez.
- **Detección de OS**: Lógica funcional en `ensure_engine()` que maneja descargas de `.zip` (Windows) y `.tar` (Unix).

---

## Créditos
- **FreeSimpleGUI**: Basado en la evolución de PySimpleGUI.
- **Python-Chess**: El corazón lógico del juego.
- **Stockfish**: El motor de ajedrez más potente del mundo.
- **Python-Easy-Chess-GUI**: Proyecto original. Fork de https://github.com/fsmosca/Python-Easy-Chess-GUI
---

*Proyecto optimizado para claridad, robustez y facilidad de exportación.*
