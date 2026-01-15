import os          # para manejar rutas de archivos y carpetas
import threading   # para ejecutar el motor en segundo plano
import queue       # para comunicacion entre hilos
import time        # para pausas (sleep) en errores visuales
import chess       # libreria de ajedrez con todas las reglas
import chess.engine # para conectar con el motor Stockfish
import FreeSimpleGUI as sg  # para crear la interfaz grafica
import platform    # para detectar sistema operativo
import zipfile     # para descomprimir archivos zip
import tarfile     # para descomprimir archivos tar
import shutil      # para mover y copiar archivos
import urllib.request  # para descargar el motor de internet

# --- SECCION 1: CONFIGURACION INICIAL DEL PROGRAMA ---

# Nombre que aparece en la ventana del juego
APP_TITLE = 'Ajedrez'

# Ruta donde estan guardadas las imagenes de las piezas
IMG_PATH = 'Images/60'

# Carpeta donde se guardara el motor de ajedrez (cerebro del bot)
ENGINE_FOLDER = "engines"

# Nombre del archivo del motor segun el sistema operativo
# En Windows se llama stockfish.exe y en Linux solo stockfish
ENGINE_NAME = "stockfish.exe" if platform.system() == "Windows" else "stockfish"

# Ruta completa al motor combinando carpeta y nombre
ENGINE_PATH = os.path.join(ENGINE_FOLDER, ENGINE_NAME)

# Diccionario con todos los colores que usa el programa
# Cada color tiene un nombre descriptivo y su codigo hexadecimal
COLORS = {
    "LIGHT": "#FFFFFF",      # casillas blancas del tablero
    "DARK": "#757575",       # casillas negras del tablero
    "SELECTED": "#00BCD4",   # casilla que el jugador selecciono
    "VALID_LIGHT": "#66BB6A", # movimiento valido en casilla blanca
    "VALID_DARK": "#2E7D32",  # movimiento valido en casilla negra
    "CAPTURE": "#FFFF00",     # movimiento que captura una pieza
    "SPECIAL": "#FF00FF",     # movimientos especiales como enroque
    "SUGGESTED_P1": "#00FFFF", # sugerencia del asistente para jugador 1
    "SUGGESTED_P2": "#AA00FF", # sugerencia del asistente para jugador 2
    "ERROR": "#FF0000"         # color cuando hay un error
}

# Diccionario que relaciona cada pieza con su imagen
# Las letras minusculas son piezas negras y mayusculas son blancas
PIECE_IMAGES = {
    'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
    'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png'
}

# --- SECCION 2: VARIABLES GLOBALES DEL JUEGO ---

# Objeto que representa el tablero de ajedrez con todas sus reglas
board = chess.Board()

# Cola para recibir movimientos del bot (como una fila de espera)
move_queue = queue.Queue()

# Cola para recibir sugerencias del asistente
suggestion_queue = queue.Queue()

# Casilla que el jugador tiene seleccionada actualmente
selected_square = None

# Diccionario con los movimientos validos desde la casilla seleccionada
valid_moves_squares = {}

# Movimiento que el motor sugiere al jugador
engine_suggestion = None

# Indica si el modo bot esta activado
is_bot_enabled = False

# Indica si el asistente esta activado
is_assistant_enabled = False

# Conjunto de botones que estan esperando confirmacion
confirm_states = set()

# Indica si ya se mostro el mensaje de fin de juego
game_over_notified = False

# --- SECCION 3: FUNCIONES AUXILIARES ---

def reset_selection():
    # Limpia todas las variables de seleccion
    # Se usa cuando el jugador hace un movimiento o cancela
    global selected_square, valid_moves_squares
    selected_square = None
    valid_moves_squares = {}
    # NO limpiamos engine_suggestion aqui para que persista

def get_sq_color(sq_idx):
    # Calcula que color debe tener cada casilla del tablero
    # Recibe el indice de la casilla y devuelve un color
    
    # Obtiene la fila y columna de la casilla
    sq_rank, sq_file = chess.square_rank(sq_idx), chess.square_file(sq_idx)
    
    # Calcula si es casilla oscura o clara del tablero
    is_dark = (sq_rank + sq_file) % 2 == 0
    
    # Asigna color base segun si es oscura o clara
    base = COLORS["DARK"] if is_dark else COLORS["LIGHT"]

    # PRIORIDAD 1: Si es la casilla seleccionada la pinta de color cyan
    if sq_idx == selected_square:
        return COLORS["SELECTED"]

    # PRIORIDAD 2: Capturas y movimientos especiales tienen alta prioridad
    if sq_idx in valid_moves_squares:
        move = valid_moves_squares[sq_idx]
        # Si el movimiento captura una pieza la pinta amarilla
        if board.is_capture(move): 
            return COLORS["CAPTURE"]
        # Si es movimiento especial la pinta magenta
        if board.is_en_passant(move) or board.is_castling(move): 
            return COLORS["SPECIAL"]

    # PRIORIDAD 3: Si el asistente esta activo y hay una sugerencia
    # El color del asistente tiene prioridad sobre movimientos validos normales
    if is_assistant_enabled and engine_suggestion and engine_suggestion in board.legal_moves:
        # Pinta las casillas de origen y destino de la sugerencia
        if sq_idx in (engine_suggestion.from_square, engine_suggestion.to_square):
            # No muestra sugerencia cuando es turno del bot
            if not (is_bot_enabled and board.turn == chess.BLACK):
                # Color diferente segun quien juega
                return COLORS["SUGGESTED_P1"] if board.turn == chess.WHITE else COLORS["SUGGESTED_P2"]
    
    # PRIORIDAD 4: Movimientos validos normales (verde)
    if sq_idx in valid_moves_squares:
        # Movimientos normales usan verde claro u oscuro
        return COLORS["VALID_DARK"] if is_dark else COLORS["VALID_LIGHT"]
    
    # Si no es ninguno de los casos anteriores usa color base
    return base

def update_ui(window):
    # Actualiza toda la interfaz grafica del programa
    # Se llama cada vez que algo cambia en el juego
    global game_over_notified
    
    # Determina el texto del jugador 2 segun el modo
    p2_label = "BOT" if is_bot_enabled else "JUGADOR 2"
    
    # Actualiza las etiquetas de los jugadores
    window['-LABEL-P1-'].update("JUGADOR 1")
    window['-LABEL-P2-'].update(p2_label)

    # Recorre todas las 64 casillas del tablero
    for r in range(8):
        for f in range(8):
            # Calcula el indice de esta casilla
            sq_idx = chess.square(f, r)
            
            # Obtiene la pieza que esta en esta casilla
            piece = board.piece_at(sq_idx)
            
            # Selecciona la imagen correcta (pieza o casilla vacia)
            if piece:
                img = os.path.join(IMG_PATH, PIECE_IMAGES[piece.symbol()])
            else:
                img = os.path.join(IMG_PATH, 'blank.png')
            
            # Calcula el color de fondo de esta casilla
            current_bg = get_sq_color(sq_idx)
            
            # Actualiza el boton con la imagen y color
            window[(r, f)].update(image_filename=img, button_color=('white', current_bg))
            
            # Configura el color cuando el mouse pasa sobre la casilla
            window[(r, f)].Widget.config(activebackground=current_bg)
    
    # Actualiza los indicadores de turno (circulos de colores)
    # El circulo brilla en cyan cuando es su turno
    window['-IND-P1-'].update(text_color="#00FFFF" if board.turn == chess.WHITE else "#333333")
    window['-IND-P2-'].update(text_color="#00FFFF" if board.turn == chess.BLACK else "#333333")
    
    # Actualiza los botones que necesitan confirmacion
    for key, text in [('RESTART', 'REINICIAR'), ('EXIT', 'SALIR')]:
        # Verifica si este boton esta esperando confirmacion
        is_confirm = key in confirm_states
        # Cambia a rojo si espera confirmacion
        color = "#FF5252" if is_confirm else ('#444444' if key == 'EXIT' else '#2c3e50')
        # Cambia el texto a SEGURO si espera confirmacion
        window[key].update("¿SEGURO?" if is_confirm else text, button_color=('white', color))
    
    # Actualiza el boton de modo (vs jugador o vs bot)
    is_confirm_bot = '-TOGGLE-BOT-' in confirm_states
    color_bot = "#FF5252" if is_confirm_bot else '#2c3e50'
    text_bot = "¿SEGURO?" if is_confirm_bot else ("vs BOT" if is_bot_enabled else "vs JUGADOR")
    window['-TOGGLE-BOT-'].update(text_bot, button_color=('white', color_bot))
    
    # Actualiza el boton del asistente
    window['-ASISTENTE-'].update(
        "ASISTENTE: ON" if is_assistant_enabled else "ASISTENTE: OFF",
        button_color=('white', '#2E7D32' if is_assistant_enabled else '#2c3e50')
    )
    
    # Actualiza el boton de saltar turno
    # Se deshabilita en modo bot para evitar confusion
    window['-SKIP-'].update(
        disabled=is_bot_enabled, 
        button_color=('white', '#555555' if is_bot_enabled else '#2c3e50')
    )

    # Verifica si el juego termino y aun no se mostro el mensaje
    if board.is_game_over() and not game_over_notified:
        # Marca que ya se mostro para no repetir
        game_over_notified = True
        # Refresca la pantalla antes de mostrar popup
        window.refresh()
        
        # Obtiene el resultado del juego
        outcome = board.outcome()
        
        # Determina el mensaje segun quien gano
        if outcome.winner == chess.WHITE: 
            res = "GANO JUGADOR 1 (Blancas)"
        elif outcome.winner == chess.BLACK: 
            res = f"GANO {p2_label} (Negras)"
        else: 
            res = "EMPATE"
        
        # Muestra ventana emergente con el resultado
        sg.popup(f"¡FIN DEL JUEGO!\n\n{res}", title="Resultado", font=('Helvetica', 12, 'bold'), keep_on_top=True)

def engine_thread_func(current_board, q):
    # Funcion que se ejecuta en un hilo separado
    # Calcula el mejor movimiento sin congelar la interfaz
    try:
        # Abre conexion con el motor de ajedrez
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
            # Verifica si hay movimientos nulos en el historial
            if any(m == chess.Move.null() for m in current_board.move_stack):
                # Crea tablero nuevo desde la posicion actual
                temp_board = chess.Board(current_board.fen())
            else:
                # Usa el tablero directamente
                temp_board = current_board
            
            # Le pide al motor que calcule el mejor movimiento
            # Limite de 0.4 segundos para que sea rapido
            result = engine.play(temp_board, chess.engine.Limit(time=0.4))
            
            # Pone el resultado en la cola para que el programa principal lo use
            q.put(result.move)
    except Exception as e:
        # Si hay error lo muestra en la terminal
        print(f"[Engine Error] {e}")

# --- SECCION 4: FUNCIONES DE DESCARGA DEL MOTOR ---

def get_engine_url():
    # Determina cual version de Stockfish descargar
    # Depende del sistema operativo y procesador
    
    # Obtiene informacion del sistema
    system = platform.system()
    machine = platform.machine().lower()
    
    # URL base donde estan las descargas
    base = "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/"
    
    # Si es Windows descarga la version para Windows
    if system == "Windows":
        return "stockfish.exe", base + "stockfish-windows-x86-64-avx2.zip"
    
    # Si es Linux verifica si es procesador ARM
    elif system == "Linux":
        if "aarch64" in machine or "arm" in machine:
            print(f"Sistema ARM detectado: {machine}")
            # En ARM intenta usar Stockfish del sistema
            system_stockfish = "/usr/games/stockfish"
            if os.path.exists(system_stockfish):
                print(f"Usando Stockfish del sistema: {system_stockfish}")
                return "stockfish", None
            # Si no esta instalado muestra mensaje de ayuda
            print("ADVERTENCIA: Stockfish no encontrado. Instalar con: sudo apt-get install stockfish")
            return None, None
        # Para procesadores normales descarga version x86
        return "stockfish", base + "stockfish-ubuntu-x86-64-avx2.tar"
    
    # Si no es Windows ni Linux no hace nada
    return None, None

def ensure_engine():
    # Verifica que el motor este instalado
    # Si no lo esta lo descarga automaticamente
    
    # Crea la carpeta de motores si no existe
    if not os.path.exists(ENGINE_FOLDER):
        os.makedirs(ENGINE_FOLDER)
    
    # Obtiene la URL de descarga correcta
    exe_name, url = get_engine_url()
    if not exe_name: 
        return None
    
    # Construye la ruta completa al motor
    target_path = os.path.normpath(os.path.join(ENGINE_FOLDER, exe_name))
    
    # Si URL es None significa que debe usar motor del sistema (ARM)
    if url is None:
        system_stockfish = "/usr/games/stockfish"
        if os.path.exists(system_stockfish):
            return system_stockfish
        return None
    
    # Si el motor ya existe solo le da permisos
    if os.path.exists(target_path) and os.path.isfile(target_path):
        if platform.system() != "Windows":
            os.chmod(target_path, 0o755)
        return target_path
    
    # Si llega aqui necesita descargar
    print(f"Descargando Stockfish para {platform.system()}...")
    sg.popup_quick_message("Descargando motor...", background_color='#333333')
    
    try:
        # Nombre del archivo temporal segun tipo
        temp_name = "temp_engine.zip" if ".zip" in url else "temp_engine.tar"
        temp_path = os.path.join(ENGINE_FOLDER, temp_name)
        
        # Descarga el archivo
        urllib.request.urlretrieve(url, temp_path)
        
        # Carpeta temporal para extraer
        extract_dir = os.path.join(ENGINE_FOLDER, "temp_extraction")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        
        # Extrae el archivo segun su tipo
        if temp_path.endswith(".zip"):
            with zipfile.ZipFile(temp_path, 'r') as z: 
                z.extractall(extract_dir)
        else:
            with tarfile.open(temp_path, 'r') as t: 
                t.extractall(extract_dir)
        
        # Busca el ejecutable de Stockfish en las carpetas extraidas
        found_bin_path = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                # Busca archivo que contenga stockfish y no sea documentacion
                if "stockfish" in file.lower() and not file.endswith(('.txt', '.md', '.zip', '.tar')):
                    found_bin_path = os.path.join(root, file)
                    break
            if found_bin_path: 
                break

        # Si encontro el ejecutable lo mueve a su ubicacion final
        if found_bin_path:
            # Borra el archivo anterior si existe
            if os.path.exists(target_path):
                if os.path.isdir(target_path): 
                    shutil.rmtree(target_path)
                else: 
                    os.remove(target_path)
            
            # Mueve el ejecutable a su ubicacion final
            shutil.move(found_bin_path, target_path)
            
            # Limpia archivos temporales
            shutil.rmtree(extract_dir)
            if os.path.exists(temp_path): 
                os.remove(temp_path)
            
            # Da permisos de ejecucion en Linux
            if platform.system() != "Windows":
                os.chmod(target_path, 0o755)
            
            return target_path
    except Exception as e:
        print(f"Error descarga: {e}")
    
    return None

# --- SECCION 5: FUNCION PRINCIPAL ---

def main():
    # Funcion principal que inicia todo el programa
    
    # Permite modificar las variables globales
    global selected_square, valid_moves_squares, is_bot_enabled, is_assistant_enabled, engine_suggestion, game_over_notified, ENGINE_PATH
    
    # Verifica que el motor este instalado
    engine_found = ensure_engine()
    if engine_found:
        ENGINE_PATH = engine_found
    else:
        # Si no hay motor muestra error y sale
        sg.popup_error("No se pudo configurar el motor")
        return

    # Establece el tema visual oscuro
    sg.theme('DarkGrey15')
    
    # Crea la matriz de botones del tablero (8x8)
    # Se crea de abajo hacia arriba (rango 7 a 0) para que coincida con ajedrez
    board_layout = [[sg.Button('', size=(4, 2), key=(r, f), border_width=0, pad=(0,0)) for f in range(8)] for r in range(7, -1, -1)]

    # Layout completo de la ventana
    layout = [
        # Fila superior con indicador y etiqueta del jugador 2
        [sg.Push(), sg.Text('●', key='-IND-P2-', font=(24), pad=(0,10)), sg.Text('', key='-LABEL-P2-', font=('Helvetica', 11, 'bold'), pad=(5,10)), sg.Push()],
        
        # Tablero de ajedrez
        [sg.Push(), sg.Column(board_layout, background_color='#000000', pad=(0, 0)), sg.Push()],
        
        # Fila inferior con indicador y etiqueta del jugador 1
        [sg.Push(), sg.Text('●', key='-IND-P1-', font=(24), pad=(0,10)), sg.Text('', key='-LABEL-P1-', font=('Helvetica', 11, 'bold'), pad=(5,10)), sg.Push()],
        
        # Fila de botones principales
        [sg.Push(), 
         sg.Button('REINICIAR', key='RESTART', size=(10, 1), pad=(3,3)), 
         sg.Button('', key='-TOGGLE-BOT-', size=(12, 1), pad=(3,3)), 
         sg.Button('', key='-ASISTENTE-', size=(14, 1), pad=(3,3)), sg.Push()],
        
        # Fila de botones secundarios
        [sg.Push(), 
         sg.Button('CARGAR FEN', key='-SET-BOARD-', size=(12, 1), pad=(3,3)), 
         sg.Button('SALTAR TURNO', key='-SKIP-', size=(12, 1), pad=(3,3)), 
         sg.Button('SALIR', key='EXIT', size=(8, 1), pad=(3,3)), sg.Push()]
    ]

    # Crea la ventana con el layout definido
    window = sg.Window(APP_TITLE, layout, finalize=True, element_justification='c', margins=(0,0))
    
    # Configura cada casilla del tablero
    for r in range(8):
        for f in range(8):
            # Obtiene el color inicial de esta casilla
            current_bg = get_sq_color(chess.square(f, r))
            # Configura propiedades especiales del boton
            window[(r, f)].Widget.config(
                takefocus=0,  # no acepta foco del teclado
                activebackground=current_bg,  # color al hacer clic
                activeforeground='white'  # color del texto al hacer clic
            )
    
    # Actualiza la interfaz por primera vez
    update_ui(window)

    # Bucle principal del programa (se repite mientras la ventana este abierta)
    while True:
        # Lee eventos de la interfaz cada 100 milisegundos
        # Para Raspberry Pi: 100ms es buen balance entre respuesta y CPU
        event, values = window.read(timeout=100)
        
        # Si se cierra la ventana sale del bucle
        if event == sg.WIN_CLOSED: 
            break

        # Manejo de botones que necesitan confirmacion
        if event in ('RESTART', 'EXIT', '-TOGGLE-BOT-'):
            # Si es el primer clic pide confirmacion
            if event not in confirm_states:
                confirm_states.clear()
                confirm_states.add(event)
                update_ui(window)
                continue
            # Si es el segundo clic ejecuta la accion
            else:
                confirm_states.clear()
                
                # Sale del programa
                if event == 'EXIT': 
                    break
                
                # Reinicia el juego
                if event == 'RESTART':
                    board.reset()
                    game_over_notified = False
                
                # Cambia entre modo jugador y bot
                if event == '-TOGGLE-BOT-':
                    is_bot_enabled = not is_bot_enabled
                    board.reset()
                    game_over_notified = False
                
                # Limpia la seleccion actual
                reset_selection()
                update_ui(window)
                
                # Si el asistente esta activo lo reactiva
                if is_assistant_enabled and not board.is_game_over() and not (is_bot_enabled and board.turn == chess.BLACK):
                    threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
                continue

        # Limpia confirmaciones si se hace cualquier otra accion
        if event not in (None, sg.TIMEOUT_EVENT):
            confirm_states.clear()

        # Boton de saltar turno
        if event == '-SKIP-':
            # Hace un movimiento nulo (pasa el turno)
            board.push(chess.Move.null())
            reset_selection()
            update_ui(window)
            # Si es modo bot inicia su movimiento
            if is_bot_enabled and board.turn == chess.BLACK:
                threading.Thread(target=engine_thread_func, args=(board.copy(), move_queue), daemon=True).start()
            # Si el asistente esta activo recalcula sugerencia
            elif is_assistant_enabled:
                threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
            continue

        # Boton de cargar posicion FEN
        if event == '-SET-BOARD-':
            # Pide al usuario que ingrese una cadena FEN
            fen = sg.popup_get_text("Posicion FEN:", title="Cargar")
            if fen:
                try:
                    # Intenta cargar la posicion
                    board.set_fen(fen)
                    reset_selection()
                    game_over_notified = False
                    update_ui(window)
                    # Si es turno del bot lo activa
                    if is_bot_enabled and board.turn == chess.BLACK and not board.is_game_over():
                        threading.Thread(target=engine_thread_func, args=(board.copy(), move_queue), daemon=True).start()
                except:
                    # Si el FEN es invalido muestra error
                    sg.popup_error("FEN Invalido")
            continue

        # Boton de activar asistente
        if event == '-ASISTENTE-':
            # Cambia el estado del asistente
            is_assistant_enabled = not is_assistant_enabled
            # Si se activo calcula primera sugerencia
            if is_assistant_enabled and not board.is_game_over() and not (is_bot_enabled and board.turn == chess.BLACK):
                threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
            else:
                # Si se desactivo borra la sugerencia
                engine_suggestion = None
            update_ui(window)
            continue

        # Manejo de clics en las casillas del tablero
        if isinstance(event, tuple) and not board.is_game_over():
            # No permite clicks si es turno del bot
            if is_bot_enabled and board.turn == chess.BLACK: 
                continue
            
            # Convierte las coordenadas del clic a indice de casilla
            sq = chess.square(event[1], event[0])
            
            # Si no hay casilla seleccionada (primer clic)
            if selected_square is None:
                # Obtiene la pieza en esta casilla
                piece = board.piece_at(sq)
                
                # Si hay pieza y es del turno actual
                if piece and piece.color == board.turn:
                    # Selecciona esta casilla
                    selected_square = sq
                    # Calcula todos los movimientos validos desde aqui
                    valid_moves_squares = {m.to_square: m for m in board.legal_moves if m.from_square == sq}
                
                # Si hay pieza pero no es del turno actual
                elif piece:
                    sg.popup_quick_message("Turno incorrecto", background_color='red', text_color='white')
            
            # Si ya hay casilla seleccionada (segundo clic)
            else:
                # Si hace clic en la misma casilla cancela la seleccion
                if sq == selected_square:
                    reset_selection()
                    update_ui(window)
                    continue

                # Busca si existe un movimiento valido a esta casilla
                move = next((m for m in board.legal_moves if m.from_square == selected_square and m.to_square == sq), None)
                
                # Si el movimiento es valido
                if move:
                    # Si es peon que llega al final lo promociona a reina
                    if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0, 7):
                        move.promotion = chess.QUEEN
                    
                    # Ejecuta el movimiento en el tablero
                    board.push(move)
                    reset_selection()
                    
                    # Si el juego no termino activa bot o asistente
                    if not board.is_game_over():
                        if is_bot_enabled and board.turn == chess.BLACK:
                            threading.Thread(target=engine_thread_func, args=(board.copy(), move_queue), daemon=True).start()
                        elif is_assistant_enabled:
                            threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
                
                # Si el movimiento no es valido
                else:
                    # Pinta la casilla de rojo
                    window[event].update(button_color=('white', COLORS["ERROR"]))
                    window[event].Widget.config(activebackground=COLORS["ERROR"])
                    # Actualiza la pantalla para que se vea el rojo
                    window.refresh()
                    # Muestra mensaje de error
                    sg.popup_quick_message("MOVIMIENTO INVALIDO", text_color='white', background_color=COLORS["ERROR"])
                    # Espera un poco para que el usuario lo vea
                    time.sleep(0.3)
                    # Limpia la seleccion
                    reset_selection()
            
            # Actualiza la interfaz
            update_ui(window)

        # Verifica si el bot termino de calcular su movimiento
        try:
            # Intenta obtener movimiento de la cola sin esperar
            bot_move = move_queue.get_nowait()
            # Ejecuta el movimiento del bot
            board.push(bot_move)
            # Borra la sugerencia anterior
            engine_suggestion = None
            # Si el asistente esta activo calcula nueva sugerencia
            if is_assistant_enabled and not board.is_game_over():
                threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
            update_ui(window)
        except queue.Empty:
            # Si no hay movimiento del bot continua
            pass

        # Verifica si hay nueva sugerencia del asistente
        try:
            # Intenta obtener sugerencia de la cola
            new_sugg = suggestion_queue.get_nowait()
            # Verifica que la sugerencia sea legal
            if new_sugg in board.legal_moves:
                engine_suggestion = new_sugg
                update_ui(window)
        except queue.Empty:
            # Si no hay sugerencia continua
            pass

    # Cierra la ventana al salir del bucle
    window.close()

# Punto de entrada del programa
if __name__ == '__main__':
    main()
