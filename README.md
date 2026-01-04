# Python Easy Chess GUI

Una interfaz grafica para ajedrez (GUI) desarrollada en Python utilizando los modulos `FreeSimpleGUI` (anteriormente `PySimpleGUI`) y `python-chess`. Este programa permite a los usuarios jugar contra motores de ajedrez UCI, gestionar repertorios de partidas y analizar posiciones con herramientas avanzadas.

Este programa esta basado en un [demo de ajedrez contra IA](https://github.com/PySimpleGUI/PySimpleGUI/tree/master/Chess) de `PySimpleGUI`.

Nota: Este fork del proyecto [Python Easy Chess GUI](https://github.com/fsmosca/Python-Easy-Chess-GUI) tiene como objetivo agregar la funcionalidad de mostrar los movimientos posibles en el tablero de la interfaz y tambien utlizar el codigo para que pueda ser integrado con un microcontrolador (esp32) para reflejar los movimientos en un tablero de ajedrez simulado de manera digital con luces leds.

---

## A. Requisitos del Sistema

Para ejecutar el programa, se requiere lo siguiente:

* **Python 3.7** o superior.
* **python-chess** v0.28.0 o superior (`pip install python-chess`).
* **FreeSimpleGUI** (`pip install FreeSimpleGUI`).
* **Pyperclip** (`pip install pyperclip`).
* Los directorios `Images`, `Engines`, `Icon` y `Book` incluidos en este repositorio.

## Instalación en Linux

Antes de instalar las dependencias de Python, asegúrate de tener los paquetes básicos:

```bash
sudo apt install python3
sudo apt install python3-pip
sudo apt install python3-tk
```

> **Nota para usuarios de Linux:**  
> En muchas distribuciones, el paquete base `python3` no incluye herramientas adicionales como `pip` ni el módulo `tkinter`.  
> Por eso es necesario instalar explícitamente `python3-pip` y `python3-tk` usando el gestor de paquetes de tu distribución (por ejemplo `apt` en Debian/Ubuntu).
> En otras distribuciones, los nombres de los paquetes pueden variar.

---

## B. Caracteristicas Detalladas

### 1. Gestion de Partidas y Repertoios PGN
El programa guarda automaticamente todas las partidas jugadas en el archivo `pecg_auto_save_games.pgn`. Ademas, permite guardar partidas especificas en:
* **Mis Juegos**: Repertoio personal general.
* **Repertorio de Blancas/Negras**: Archivos dedicados para estudiar aperturas o lineas especificas.

### 2. Soporte para Motores UCI
Puedes instalar cualquier motor compatible con el protocolo UCI (como Stockfish).
* **Instalacion**: Ve a `Engine -> Manage -> Install` en modo Neutral.
* **Configuracion**: Es posible editar parametros internos del motor (como Hash, Threads, etc.) mediante `Engine -> Manage -> Edit`.

### 3. Asistencia de Libros de Aperturas (Polyglot)
El programa admite el uso de libros de aperturas en formato `.bin`.
* Puedes ver las jugadas sugeridas por el libro haciendo clic derecho en las etiquetas de `BOOK` y seleccionando `Show`.
* Permite configurar libros distintos para el motor y para consulta del usuario.

### 4. Analisis con Motor Consejero (Adviser)
Ademas del motor oponente, puedes configurar un "Adviser" (Consejero). Al activarlo con clic derecho en `Adviser -> Start`, el motor analizara la posicion actual permanentemente y mostrara la evaluacion y la linea principal.

---

## C. Guia de Instalacion Paso a Paso

1. **Desde el Codigo Fuente**:
   * Descarga todos los archivos del repositorio, manteniendo la estructura de carpetas.
   * Instala las dependencias:
     ```bash
     pip install python-chess FreeSimpleGUI pyperclip
     ```
     o

     ```bash
     pip install -r requirements.txt
     ```
   * Coloca tus motores UCI favoritos en la carpeta `Engines`.

2. **Uso en Linux**:
   Asegurate de dar permisos de ejecucion a los motores UCI con el comando:
   `chmod +x nombre_del_motor`.

---

## D. Como Utilizar el Programa

### Modos de Operacion
La GUI tiene dos modos principales:
1. **Neutral**: Para configuracion de motores, colores, temas y opciones de tiempo.
2. **Play**: Para jugar la partida activamente.

### Para Jugar como Blancas
* Cambia a `Mode -> Play`.
* Haz clic en la pieza y luego en la casilla de destino.

### Para Jugar como Negras
* En modo Neutral, ve a `Board -> Flip` para que las piezas negras esten abajo.
* Cambia a `Mode -> Play`.
* Ve a `Engine -> Go` para que el motor realice la primera jugada de las blancas.

### Funciones de Analisis y FEN
* **Pegar FEN**: Puedes cargar una posicion desde el portapapeles en `FEN -> Paste` (debe estar en modo `Play`).
* **Ver Info de Busqueda**: Haz clic derecho sobre la etiqueta de informacion del oponente y selecciona `Show` para ver profundidad, puntaje y tiempo.

### Configuracion de Tiempo
* **Time -> Engine**: Define el tiempo disponible para el motor (soporta incrementos Fischer, Delay y Classical).
* **Time -> User**: Define tu propio tiempo.

---

## E. Personalizacion Visual
En modo Neutral, puedes cambiar la apariencia del tablero:
* **Board -> Color**: Elige entre varios colores de casillas (Marron, Azul, Verde, Gris).
* **Board -> Theme**: Selecciona temas visuales predefinidos para la interfaz.

---

## F. Creditos y Librerias
* **FreeSimpleGUI**: Biblioteca principal para la interfaz grafica.
* **Python-Chess**: Motor logico para el manejo de reglas de ajedrez y protocolos UCI.
* **Pyperclip**: Gestion del portapapeles para copiar/pegar FEN y PGN.
* **PyInstaller**: Utilizado para la creacion del archivo ejecutable.
* **pgn-extract**: Utilidad recomendada para el manejo avanzado de archivos PGN.
* **Codigo fuente**: [Repositorio GitHub de Ferdinand Mosca](https://github.com/fsmosca/Python-Easy-Chess-GUI)
