#!/usr/bin/env python3
import os
import threading
import queue
import time
import chess
import chess.engine
import FreeSimpleGUI as sg

# --- 1 CONFIGURACIONES Y COLORES ---
APP_TITLE = 'Sun & Moon Chess - Proyecto Final'
IMG_PATH = 'Images/60'
ENGINE_PATH = "engines/stockfish.exe" 

COLORS = {
    "BG_APP": "#1A1A1A",
    "LIGHT": "#FFFFFF",
    "DARK": "#757575",
    "SELECTED": "#00BCD4",
    "CONFIRM": "#FF5252",
    "BUTTON_NORMAL": "#2c3e50",
    "VALID_LIGHT": "#66BB6A",
    "VALID_DARK": "#2E7D32",
    "CAPTURE": "#FFFF00",
    "SPECIAL": "#FF00FF",
    "SUGGESTED_P1": "#00FFFF",
    "SUGGESTED_P2": "#AA00FF",
    "INDICATOR_ON": "#00FFFF",
    "INDICATOR_OFF": "#333333",
    "ERROR": "#D32F2F"
}

PIECE_IMAGES = {
    'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
    'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png'
}

# --- 2 ESTADO GLOBAL ---
board = chess.Board()
move_queue = queue.Queue()
suggestion_queue = queue.Queue()
selected_square = None
valid_moves_squares = {}
engine_suggestion = None
is_bot_enabled = False
is_assistant_enabled = False
confirm_states = set()
game_over_notified = False # controla que la notificacion de fin solo salga una vez

# --- 3 FUNCIONES DE APOYO ---

def reset_selection():
    global selected_square, valid_moves_squares, engine_suggestion
    selected_square = None
    valid_moves_squares = {}
    engine_suggestion = None

def get_sq_color(sq_idx):
    # determina el color de fondo de una casilla segun su estado
    sq_rank, sq_file = chess.square_rank(sq_idx), chess.square_file(sq_idx)
    is_dark = (sq_rank + sq_file) % 2 == 0
    base = COLORS["DARK"] if is_dark else COLORS["LIGHT"]

    if sq_idx == selected_square:
        return COLORS["SELECTED"]
    
    if sq_idx in valid_moves_squares:
        move = valid_moves_squares[sq_idx]
        if board.is_capture(move): return COLORS["CAPTURE"]
        if board.is_en_passant(move) or board.is_castling(move): return COLORS["SPECIAL"]
        return COLORS["VALID_DARK"] if is_dark else COLORS["VALID_LIGHT"]
    
    is_legal_suggest = engine_suggestion and engine_suggestion in board.legal_moves
    if is_assistant_enabled and is_legal_suggest:
        if sq_idx in (engine_suggestion.from_square, engine_suggestion.to_square):
            if not (is_bot_enabled and board.turn == chess.BLACK):
                return COLORS["SUGGESTED_P1"] if board.turn == chess.WHITE else COLORS["SUGGESTED_P2"]
    return base

def update_button_confirm(window, key, text):
    # actualiza visualmente los botones que requieren doble clic
    active = key in confirm_states
    color = COLORS["CONFIRM"] if active else (COLORS["BUTTON_NORMAL"] if key != 'EXIT' else '#444444')
    window[key].update("¿SEGURO?" if active else text, button_color=('white', color))

def update_ui(window):
    # refresca toda la interfaz grafica
    global game_over_notified
    p2_label = "BOT" if is_bot_enabled else "JUGADOR 2"
    window['-LABEL-P1-'].update("JUGADOR 1")
    window['-LABEL-P2-'].update(p2_label)

    # actualiza el tablero de 8x8 sin padding
    for r in range(8):
        for f in range(8):
            sq_idx = chess.square(f, r)
            img = os.path.join(IMG_PATH, PIECE_IMAGES[board.piece_at(sq_idx).symbol()]) if board.piece_at(sq_idx) else os.path.join(IMG_PATH, 'blank.png')
            window[(r, f)].update(image_filename=img, button_color=(None, get_sq_color(sq_idx)))
    
    # indicadores de turno
    window['-IND-P1-'].update(text_color=COLORS["INDICATOR_ON"] if board.turn == chess.WHITE else COLORS["INDICATOR_OFF"])
    window['-IND-P2-'].update(text_color=COLORS["INDICATOR_ON"] if board.turn == chess.BLACK else COLORS["INDICATOR_OFF"])
    
    # estados de botones
    update_button_confirm(window, 'RESTART', 'REINICIAR')
    update_button_confirm(window, 'EXIT', 'SALIR')
    update_button_confirm(window, '-TOGGLE-BOT-', "vs BOT" if is_bot_enabled else "vs JUGADOR")
    
    asist_text = "ASISTENTE: ON" if is_assistant_enabled else "ASISTENTE: OFF"
    window['-ASISTENTE-'].update(asist_text, button_color=('white', '#2E7D32' if is_assistant_enabled else COLORS["BUTTON_NORMAL"]))
    window['-SKIP-'].update(disabled=is_bot_enabled, button_color=('white', '#555555' if is_bot_enabled else COLORS["BUTTON_NORMAL"]))

    # manejo de fin de juego con notificacion unica
    if board.is_game_over() and not game_over_notified:
        game_over_notified = True
        window.refresh()
        outcome = board.outcome()
        res = "EMPATE"
        if outcome.winner == chess.WHITE: res = "GANO JUGADOR 1 (Blancas)"
        elif outcome.winner == chess.BLACK: res = f"GANO {p2_label} (Negras)"
        sg.popup(f"¡FIN DEL JUEGO!\n\n{res}", title="Resultado", font=('Helvetica', 12, 'bold'), keep_on_top=True)

def engine_thread_func(current_board, q):
    # hilo para calculos del motor stockfish
    try:
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
            temp_board = chess.Board(current_board.fen()) if any(m == chess.Move.null() for m in current_board.move_stack) else current_board
            result = engine.play(temp_board, chess.engine.Limit(time=0.4))
            q.put(result.move)
    except: pass

# --- 4 MAIN ---

def main():
    global selected_square, valid_moves_squares, is_bot_enabled, is_assistant_enabled, engine_suggestion, game_over_notified
    sg.theme('DarkGrey15')

    # botones del tablero sin ningun tipo de padding interno
    board_layout = [[sg.Button('', size=(4, 2), key=(r, f), border_width=0, pad=(0,0)) for f in range(8)] for r in range(7, -1, -1)]

    # layout ultra compacto con ligeros margenes en etiquetas y separacion entre botones
    layout = [
        [sg.Push(), sg.Text('●', key='-IND-P2-', font=(24), pad=(0,10)), sg.Text('', key='-LABEL-P2-', font=('Helvetica', 11, 'bold'), pad=(5,10)), sg.Push()],
        [sg.Push(), sg.Column(board_layout, background_color='#000000', pad=(0, 0)), sg.Push()],
        [sg.Push(), sg.Text('●', key='-IND-P1-', font=(24), pad=(0,10)), sg.Text('', key='-LABEL-P1-', font=('Helvetica', 11, 'bold'), pad=(5,10)), sg.Push()],
        [sg.Push(), 
         sg.Button('REINICIAR', key='RESTART', size=(10, 1), pad=(3,3)), 
         sg.Button('', key='-TOGGLE-BOT-', size=(12, 1), pad=(3,3)), 
         sg.Button('', key='-ASISTENTE-', size=(14, 1), pad=(3,3)), sg.Push()],
        [sg.Push(), 
         sg.Button('CARGAR FEN', key='-SET-BOARD-', size=(12, 1), pad=(3,3)), 
         sg.Button('SALTAR TURNO', key='-SKIP-', size=(12, 1), pad=(3,3)), 
         sg.Button('SALIR', key='EXIT', size=(8, 1), pad=(3,3)), sg.Push()]
    ]

    # ventana ajustada estrictamente al contenido
    window = sg.Window(APP_TITLE, layout, finalize=True, element_justification='c', margins=(0,0))
    update_ui(window)

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED: break

        # gestion de eventos de botones con confirmacion corregida
        if event in ('RESTART', 'EXIT', '-TOGGLE-BOT-'):
            if event not in confirm_states:
                confirm_states.clear()
                confirm_states.add(event)
                update_ui(window)
                continue
            else:
                # segundo clic: ejecutar accion
                action = event
                confirm_states.clear()
                if action == 'EXIT': break
                if action == 'RESTART': 
                    board.reset()
                    game_over_notified = False
                if action == '-TOGGLE-BOT-':
                    is_bot_enabled = not is_bot_enabled
                    board.reset()
                    game_over_notified = False
                reset_selection()
                update_ui(window)
                continue

        # si se hace clic en cualquier otra cosa se limpia la espera de confirmacion
        if event is not None and event != sg.TIMEOUT_EVENT:
            confirm_states.clear()

        if event == '-SKIP-':
            board.push(chess.Move.null())
            reset_selection()
            update_ui(window)
            if is_bot_enabled and board.turn == chess.BLACK:
                threading.Thread(target=engine_thread_func, args=(board.copy(), move_queue), daemon=True).start()
            continue

        if event == '-SET-BOARD-':
            fen = sg.popup_get_text("Posicion FEN:", title="Cargar")
            if fen:
                try: 
                    board.set_fen(fen)
                    reset_selection()
                    game_over_notified = False
                    update_ui(window)
                    # dispara el bot si el turno cargado es el del bot
                    if is_bot_enabled and board.turn == chess.BLACK and not board.is_game_over():
                        threading.Thread(target=engine_thread_func, args=(board.copy(), move_queue), daemon=True).start()
                except: sg.popup_error("FEN Invalido")
            continue

        if event == '-ASISTENTE-':
            is_assistant_enabled = not is_assistant_enabled
            if is_assistant_enabled and not board.is_game_over() and not (is_bot_enabled and board.turn == chess.BLACK):
                threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
            else: engine_suggestion = None
            update_ui(window)
            continue

        if isinstance(event, tuple) and not board.is_game_over():
            if is_bot_enabled and board.turn == chess.BLACK: continue
            sq = chess.square(event[1], event[0])
            
            if selected_square is None:
                piece = board.piece_at(sq)
                if piece and piece.color == board.turn:
                    selected_square = sq
                    valid_moves_squares = {m.to_square: m for m in board.legal_moves if m.from_square == sq}
                elif piece: sg.popup_quick_message("Turno incorrecto", background_color='red')
            else:
                move = next((m for m in board.legal_moves if m.from_square == selected_square and m.to_square == sq), None)
                if move:
                    if board.piece_at(selected_square).piece_type == chess.PAWN and chess.square_rank(move.to_square) in (0, 7):
                        move.promotion = chess.QUEEN
                    board.push(move)
                    reset_selection()
                    if not board.is_game_over():
                        target_q = move_queue if is_bot_enabled else (suggestion_queue if is_assistant_enabled else None)
                        if target_q: threading.Thread(target=engine_thread_func, args=(board.copy(), target_q), daemon=True).start()
                else:
                    window[event].update(button_color=('white', COLORS["ERROR"]))
                    window.refresh()
                    time.sleep(0.1)
                    selected_square = None
                    valid_moves_squares = {}
            update_ui(window)

        # procesar colas de motor
        try:
            bot_move = move_queue.get_nowait()
            board.push(bot_move)
            engine_suggestion = None
            if is_assistant_enabled and not board.is_game_over():
                threading.Thread(target=engine_thread_func, args=(board.copy(), suggestion_queue), daemon=True).start()
            update_ui(window)
        except queue.Empty: pass

        try:
            new_sugg = suggestion_queue.get_nowait()
            if new_sugg in board.legal_moves:
                engine_suggestion = new_sugg
                update_ui(window)
        except queue.Empty: pass

    window.close()

if __name__ == '__main__':
    main()
