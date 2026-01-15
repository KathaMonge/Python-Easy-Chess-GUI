# Python Easy Chess GUI (Fork español y simplificado)

Una interfaz gráfica de ajedrez compacta y funcional desarrollada en Python. Esta versión ha sido simplificada drásticamente para enfocarse en la facilidad de uso, la automatización y la integración futura con hardware (LEDs en Raspberry Pi).

<br>
<p align="center">
    <img width="485" height="657" alt="SS NEW UI" src="https://github.com/user-attachments/assets/07d30ff2-c567-4d01-a711-716a813b0633" />
</p>

---

## Características Principales

- **Descarga Automática de Motor**: No necesitas buscar Stockfish manualmente. El programa detecta automáticamente tu sistema operativo (Windows, Linux) y arquitectura (x64, ARM) y descarga la versión correcta de Stockfish 16.
  - **Soporte ARM**: En Raspberry Pi y sistemas ARM, detecta si Stockfish está instalado en el sistema (`/usr/games/stockfish`) o descarga la versión apropiada.
- **Interfaz Ultra-Compacta**: Desarrollada con `FreeSimpleGUI`, diseñada para ser ligera, rápida y directa.

- **Modos de Juego**:

  - **vs JUGADOR**: Juega localmente contra otra persona.
  - **vs BOT**: Enfrenta al motor de ajedrez Stockfish.

- **Asistente de Movimientos Inteligente**:

  - Sugerencias visuales en tiempo real sobre el tablero.
  - Muestra la mejor jugada según Stockfish con colores distintivos.
  - Funciona en ambos modos de juego.
  - Persiste entre turnos y se actualiza automáticamente.

- **Gestión de FEN**: Carga cualquier posición de ajedrez pegando una cadena FEN estándar.

- **Feedback Visual Avanzado**:

  - Resaltado de casilla seleccionada (cyan)
  - Movimientos válidos (verde)
  - Capturas (amarillo)
  - Movimientos especiales como enroque (magenta)
  - Sugerencias del asistente (cyan brillante/morado según jugador)
  - Errores de movimiento inválido (rojo intermitente)

- **Confirmación de Acciones Críticas**: Botones como "REINICIAR", "SALIR" y cambio de modo requieren doble clic para evitar acciones accidentales.

- **Saltar Turno**: Opción para pasar el turno sin mover (útil para análisis y pruebas).

---

## Requisitos e Instalación

### 1. Requisitos

- **Python 3.8 o superior**
- **Dependencias de Python**:
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

### 3. Instalación en Raspberry Pi (ARM)

Para sistemas ARM como Raspberry Pi, instala Stockfish desde los repositorios:

```bash
sudo apt-get update
sudo apt-get install stockfish
```

El programa detectará automáticamente la instalación del sistema.

---

## Instrucciones de Uso

### Inicio Rápido

1. **Ejecuta el programa**: `python kchess.py`
2. **Primera ejecución**: En el primer inicio, el programa descargará el motor Stockfish automáticamente en la carpeta `engines/`. Puede tardar unos minutos dependiendo de tu conexión.

### Controles Básicos

- **Seleccionar pieza**: Haz clic en una pieza de tu color para ver sus movimientos válidos (resaltados en verde).
- **Mover**: Haz clic en una casilla válida resaltada para mover la pieza.
- **Deseleccionar**: Haz clic nuevamente en la misma pieza para cancelar la selección.

### Funciones Avanzadas

#### Modo Bot

- Haz clic en **vs JUGADOR** para cambiar a **vs BOT**.
- Requiere confirmación (segundo clic en "¿SEGURO?").
- El bot juega automáticamente con las piezas negras.
- El juego se reinicia al cambiar de modo.

#### Asistente de Movimientos

- Activa/desactiva con el botón **ASISTENTE**.
- Cuando está activo (verde), muestra la mejor jugada sugerida por Stockfish.
- Las casillas de origen y destino se resaltan en colores distintivos.
- La sugerencia se actualiza automáticamente después de cada movimiento.
- **Prioridad de colores**: La casilla seleccionada siempre se ve en cyan, luego el asistente, luego los movimientos válidos.

#### Otras Funciones

- **CARGAR FEN**: Introduce una cadena FEN para cargar cualquier posición personalizada.
- **SALTAR TURNO**: Pasa el turno sin mover (hace un movimiento nulo).
- **REINICIAR**: Vuelve a la posición inicial (requiere confirmación).
- **SALIR**: Cierra el programa (requiere confirmación).

---

## Detalles Técnicos

### Arquitectura del Código

- **Código documentado**: Comentarios descriptivos diseñados para facilitar la comprensión y defensa del proyecto.
- **Variables globales**: Estado del juego centralizado y fácilmente accesible.
- **Función `get_sq_color()`**: Sistema de prioridades para determinar el color de cada casilla, ideal para integración con LEDs.

### Optimizaciones

- **Multihilo (Threading)**: El motor Stockfish se ejecuta en hilos separados para evitar que la interfaz se congele durante el análisis.
- **Thread-Safety**: Se utiliza `board.copy()` al pasar datos al motor para asegurar integridad de datos.
- **Loop eficiente**: Ciclo de 100ms ideal para Raspberry Pi, balanceando respuesta y uso de CPU.
- **Sin hover blanco**: Configuración especial de `activebackground` en Linux para mantener colores consistentes.

### Protocolo y Compatibilidad

- **Protocolo UCI**: Comunicación estándar con motores de ajedrez.
- **Detección de OS**: Lógica robusta en `ensure_engine()` que maneja descargas de `.zip` (Windows) y `.tar` (Linux).
- **Soporte ARM**: Detección automática de procesadores ARM y uso de Stockfish del sistema.

### Preparado para Hardware

El código está **optimizado para integración con LEDs** sin modificaciones:

- Sistema de colores hexadecimales fácilmente mapeables a RGB.
- Estado global accesible desde módulos externos.
- Función `get_sq_color()` centralizada que calcula el color de cada casilla.
- Loop constante que permite lectura de estado en tiempo real.

---

## Estructura del Proyecto

```
.
├── kchess.py          # Programa principal
├── Images/
│   └── 60/               # Imágenes de piezas (60x60px)
│       ├── bP.png        # Peón negro
│       ├── wP.png        # Peón blanco
│       └── ...
├── engines/              # Carpeta donde se descarga Stockfish
│   └── stockfish         # Motor de ajedrez (descarga automática)
└── README.md            # Este archivo
```

---

## Solución de Problemas

### El motor no descarga en ARM/Raspberry Pi

Si ves el error "HTTP Error 404: Not Found" en sistemas ARM:

```bash
sudo apt-get update
sudo apt-get install stockfish
```

El programa usará automáticamente la versión instalada en `/usr/games/stockfish`.

### La interfaz se ve mal en Linux

Asegúrate de tener instalado `python3-tk`:

```bash
sudo apt install python3-tk
```

### El asistente no muestra sugerencias

- Verifica que el motor Stockfish esté correctamente instalado.
- Revisa la consola para mensajes de error del motor.
- En ARM, asegúrate de haber instalado Stockfish con apt-get.

---

## Créditos

- **FreeSimpleGUI**: Basado en la evolución de PySimpleGUI.
- **Python-Chess**: El corazón lógico del juego de ajedrez.
- **Stockfish**: El motor de ajedrez de código abierto más potente del mundo.
- **Python-Easy-Chess-GUI**: Proyecto original - Fork de [fsmosca/Python-Easy-Chess-GUI](https://github.com/fsmosca/Python-Easy-Chess-GUI)

---

## Licencia

Este proyecto mantiene la licencia del proyecto original.

---

_Proyecto optimizado para claridad, robustez, facilidad de uso y preparado para integración con hardware (Raspberry Pi + LEDs)._
