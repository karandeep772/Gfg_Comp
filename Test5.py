import chess # type: ignore
import chess.engine #type: ignore
import chess.pgn #type: ignore
import time
import numpy as np
from pathlib import Path
from chessboard_detector import get_chessboard
import requests
import sys
import json
from ChessBoard_Creation import ChessBoard_Creation
from Chess_MoveDetection import Chess_MoveDetection
from Fen_To_Array import fen_to_array

fen_array = np.full(120, '', dtype=object)

ChessBoard_array = ChessBoard_Creation()

# def read_player_color():
#     if len(sys.argv) < 2:
#         print("Error: Player_Color argument is required.")
#         sys.exit(1)

#     try:
#         player_color = int(sys.argv[1])  # Either 0 or 1
#         if player_color not in [0, 1]:
#             raise ValueError("Player_Color must be 0 or 1")
#         return player_color
#     except (IndexError, ValueError) as e:
#         print(f"Error processing Player_Color argument: {e}")
#         sys.exit(1)

# Player_Color = read_player_color()

Player_Color = 1

# Path to the Stockfish engine executable
engine_path = r"C:\Users\karan\OneDrive\Desktop\stockfish\stockfish.exe"

# Start the engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
JC = 0
def fetch_chessboard():
    global JC
    if JC==0:
        image_path = r'C:\Users\karan\OneDrive\Desktop\\C13.jpg'
        JC += 1
    else:
        image_path = r'C:\Users\karan\OneDrive\Desktop\\C18.jpg'
    
    ChessBoard1 = get_chessboard(image_path)
    ChessBoard = [['' if piece == '*' else piece for piece in row] for row in ChessBoard1]
    return ChessBoard,ChessBoard1

def array_to_fen(ChessBoard):
    board = chess.Board(None)
    piece_map = {
        'P': 'P', 'p': 'p',
        'R': 'R', 'r': 'r',
        'N': 'N', 'n': 'n',
        'B': 'B', 'b': 'b',
        'Q': 'Q', 'q': 'q',
        'K': 'K', 'k': 'k',
        '*': None
    }
    for row in range(8):
        for col in range(8):
            piece_symbol = ChessBoard[row][col]
            if piece_symbol:
                square = chess.square(col, 7 - row)
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))
    return board.fen()

def send_fen_to_javascript(fen, pgn=None, move_count=None):
    url = 'http://localhost:3000/update_fen'
    payload = {'fen': fen}
    
    if pgn:
        payload['pgn'] = pgn
    if move_count is not None:
        payload['move_count'] = move_count
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"FEN successfully sent to JavaScript: {fen}")
    except requests.RequestException as e:
        print(f"Error sending FEN to JavaScript: {e}")

def get_best_move(board):
    try:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        board.push(move)
        return move, board
    except Exception as e:
        print(f"Error getting best move: {e}")
        return None, board

def fen_to_pgn(prev_fen, new_fen):
    board = chess.Board(prev_fen)

    for move in board.legal_moves:
        move_san = board.san(move)

        board.push(move)

        if board.fen() == new_fen:
            return move_san
        
        board.pop()

    raise ValueError(f"Could not find a valid move leading to the new FEN: {new_fen}")

def update_fen_to_move(current_fen, move_side):
    parts = current_fen.split()
    if (move_side == 'white' and parts[1] == 'b') or (move_side == 'black' and parts[1] == 'w'):
        parts[1] = 'b' if move_side == 'black' else 'w'
        return ' '.join(parts)
    else:
        return current_fen

    
def add_castling_rights(fen, castling_rights):
    parts = fen.split()
    
    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    parts[2] = castling_rights

    updated_fen = ' '.join(parts)
    return updated_fen

def increment_fen_move_count(fen, noofmoves, half_moves):
    parts = fen.split()

    if len(parts) != 6:
        raise ValueError("Invalid FEN string")

    # Move count is in the 6th field (index 5)
    move_count = int(parts[5])

    # Half-move clock is in the 5th field (index 4)
    half_move_clock = int(parts[4])

    if noofmoves % 2 == 0:
        move_count += noofmoves // 2
    else:
        move_count += 1 + (noofmoves // 2)

    half_move_clock = half_moves

    if half_moves == 0:
        half_move_clock = 0

    parts[4] = str(half_move_clock)
    parts[5] = str(move_count)
    
    updated_fen = ' '.join(parts)
    
    return updated_fen

def handle_undo_request():
    global previous_fen, move_count, ChessBoard_array,current_fen,Player_Color,previous_black_fen,previous_white_fen
    if previous_fen:
        # if move_count==2 or move_count==1:
        #     ChessBoard_array = ChessBoard_Creation()
        #     fen_to_send = fen_to_array(ChessBoard_array)
        #     previous_fen = fen_to_array(ChessBoard_array)
        #     current_fen = fen_to_array(ChessBoard_array)
        #     previous_white_fen = ChessBoard_Creation()
        #     previous_black_fen = ChessBoard_Creation()
        #     send_fen_to_javascript(fen_to_send,pgn,move_count)
        #     move_count = 0
        #     return
        # elif move_count == 3:
        #     fen_to_send = fen_array[1]
        #     ChessBoard_array = ChessBoard_Creation()
        #     previous_fen = fen_to_array(ChessBoard_array)
        #     current_fen = fen_to_send
        #     previous_white_fen = ChessBoard_Creation()
        #     previous_black_fen = ChessBoard_Creation()
        #     send_fen_to_javascript(fen_to_send,pgn,move_count)
        #     move_count = 0
        #     return
        # # Use previous_fen to revert to the last known good state
        # else:
        fen_to_send = fen_array[move_count-3]
        # ChessBoard_array = fen_to_array(previous_fen)
        
        if Player_Color == 1:
            print("Inside undo function")
            previous_fen = fen_array[move_count-3]
            previous_white_fen = fen_array[move_count-4]
            previous_black_fen = fen_array[move_count-4]
        move_count -= 2
        current_fen = fen_to_send
        ChessBoard_array = fen_to_array(previous_black_fen)
        ChessBoard_Current = fen_to_array(current_fen)
        #send_fen_to_javascript(fen_to_send,pgn,move_count)
        print(move_count,"\n",current_fen,"\n",ChessBoard_array,"\n",ChessBoard_Current,"\n",previous_fen,"\n",previous_black_fen)
        time.sleep(10)
        print(f"Undo: Reverted to FEN: {fen_to_send}")

# Initialize variables
move_count = 0
game_start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
previous_fen = game_start_fen
previous_white_fen = None
previous_black_fen = None
current_fen = game_start_fen
castling_rights = 'KQkq'
Current_Half_Move = 0


try:
    while True:
        if(move_count>=5):
            handle_undo_request()
        #     response = requests.get('http://localhost:3000/check_undo')
        #     if response.status_code == 200:
        #         undo_data = response.json()
        #         if undo_data.get('undo'):
        #             handle_undo_request()
        #             # Optionally reset the undo flag on the server
        #             requests.post('http://localhost:3000/reset_undo')
        #     time.sleep(1)  # Check every second or adjust as needed
        # except requests.RequestException as e:
        #     print(f"Error checking undo: {e}")
        #     time.sleep(5)  # Wait before retrying in case of an error
        # except requests.RequestException as e:
        #     print(f"Error checking undo request: {e}")

        if Player_Color == 0:  #Player As White
            ChessBoard,ChessBoard_Current = fetch_chessboard()
            current_fen = array_to_fen(ChessBoard)

            if current_fen != previous_fen and previous_white_fen != current_fen:
                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1

                previous_white_fen = current_fen
                current_fen = add_castling_rights(current_fen, castling_rights)
                current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)
                move_count += 1
                current_fen = update_fen_to_move(current_fen, 'black')
                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #print(f"PGN from previous FEN to new FEN: {pgn}")
                fen_array[move_count-1] = current_fen
                #send_fen_to_javascript(current_fen, pgn, move_count)

                ChessBoard_array = ChessBoard_Current
                previous_fen = current_fen
                
                #time.sleep(10)
                board = chess.Board(current_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                previous_black_fen = current_fen
                ChessBoard_Current = fen_to_array(current_fen)

                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1
                current_fen = add_castling_rights(current_fen, castling_rights)
                ChessBoard_array = ChessBoard_Current

                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #print(f"PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                #send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = current_fen


        elif Player_Color == 1:  #Player as Black
            if move_count == 0:
                board = chess.Board(game_start_fen)
                best_move, updated_board = get_best_move(board)
                current_fen = updated_board.fen()
                ChessBoard_Current = fen_to_array(current_fen)
                previous_white_fen = current_fen
                Piece_Moved = ""
                Piece_Captured = ""
                Castling = ""
                Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                if(no_of_rooks<4):
                    if ChessBoard_Current[0][0]!='r':
                        castling_rights ==castling_rights.replace("q","") 
                    if ChessBoard_Current[0][7]!='r':
                        castling_rights ==castling_rights.replace("k","")  
                    if ChessBoard_Current[7][0]!='R':
                        castling_rights ==castling_rights.replace("Q","") 
                    if ChessBoard_Current[7][7]!='R':
                        castling_rights ==castling_rights.replace("K","")           
                if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                    if move_count%2==0:
                        castling_rights = castling_rights.replace("KQ", "")
                    elif move_count%2!=0:
                        castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'K':
                    castling_rights = castling_rights.replace("KQ", "")
                elif Piece_Moved == 'k':
                    castling_rights = castling_rights.replace("kq", "")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("q","")
                elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("k","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                    castling_rights = castling_rights.replace("Q","")
                elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                    castling_rights = castling_rights.replace("K","")

                if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                    Current_Half_Move = 0
                elif(Piece_Captured == "x"):
                    Current_Half_Move = 0
                else:
                    Current_Half_Move += 1

                ChessBoard_array = ChessBoard_Current
                #print(current_fen)
                #print(previous_fen)
                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #print(f"In Player color1 move count 0 PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                #send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = update_fen_to_move(previous_fen,'black')
                previous_fen = current_fen
                #time.sleep(5)
            else:
                ChessBoard,ChessBoard_Current = fetch_chessboard()
                current_fen = array_to_fen(ChessBoard)

                if current_fen != previous_fen and previous_black_fen != current_fen:
                    Piece_Moved = ""
                    Piece_Captured = ""
                    Castling = ""
                    Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                    if(no_of_rooks<4):
                        if ChessBoard_Current[0][0]!='r':
                            castling_rights ==castling_rights.replace("q","") 
                        if ChessBoard_Current[0][7]!='r':
                            castling_rights ==castling_rights.replace("k","")  
                        if ChessBoard_Current[7][0]!='R':
                            castling_rights ==castling_rights.replace("Q","") 
                        if ChessBoard_Current[7][7]!='R':
                            castling_rights ==castling_rights.replace("K","")           
                    if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                        if move_count%2==0:
                            castling_rights = castling_rights.replace("KQ", "")
                        elif move_count%2!=0:
                            castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'K':
                        castling_rights = castling_rights.replace("KQ", "")
                    elif Piece_Moved == 'k':
                        castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("q","")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("k","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("Q","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("K","")

                    if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                        Current_Half_Move = 0
                    elif(Piece_Captured == "x"):
                        Current_Half_Move = 0
                    else:
                        Current_Half_Move += 1
                    move_count += 1
                    previous_black_fen = current_fen
                    print(previous_fen)
                    current_fen = add_castling_rights(current_fen, castling_rights)
                    current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)
                    print(current_fen)

                    ChessBoard_array = ChessBoard_Current

                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = pgn_moves
                    #print(f" We are here PGN from previous FEN to new FEN: {pgn}")
                    fen_array[move_count-1] = current_fen
                    #send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    previous_fen = update_fen_to_move(current_fen, 'white')
                    #print(current_fen)

                    #time.sleep(10)
                    board = chess.Board(current_fen)
                    best_move, updated_board = get_best_move(board)
                    current_fen = updated_board.fen()
                    ChessBoard_Current = fen_to_array(current_fen)
                    #print(current_fen)
                    #print(previous_fen)
                    previous_white_fen = current_fen
                    

                    Piece_Moved = ""
                    Piece_Captured = ""
                    Castling = ""
                    Sq, Piece_Moved, Piece_Captured, Castling, no_of_rooks = Chess_MoveDetection(ChessBoard_Current, ChessBoard_array)
                    if(no_of_rooks<4):
                        if ChessBoard_Current[0][0]!='r':
                            castling_rights ==castling_rights.replace("q","") 
                        if ChessBoard_Current[0][7]!='r':
                            castling_rights ==castling_rights.replace("k","")  
                        if ChessBoard_Current[7][0]!='R':
                            castling_rights ==castling_rights.replace("Q","") 
                        if ChessBoard_Current[7][7]!='R':
                            castling_rights ==castling_rights.replace("K","")           
                    if Castling == "O-O" or Castling == "O-O-O" or Castling == "o-o" or Castling == "o-o-o":
                        if move_count%2==0:
                            castling_rights = castling_rights.replace("KQ", "")
                        elif move_count%2!=0:
                            castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'K':
                        castling_rights = castling_rights.replace("KQ", "")
                    elif Piece_Moved == 'k':
                        castling_rights = castling_rights.replace("kq", "")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==0) or (Sq[1][0]==0 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("q","")
                    elif Piece_Moved == 'r' and ((Sq[0][0]==0 and Sq[0][1]==7) or (Sq[1][0]==0 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("k","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==0) or (Sq[1][0]==7 and Sq[1][1]==0)):
                        castling_rights = castling_rights.replace("Q","")
                    elif Piece_Moved == 'R' and ((Sq[0][0]==7 and Sq[0][1]==7) or (Sq[1][0]==7 and Sq[1][1]==7)):
                        castling_rights = castling_rights.replace("K","")

                    if(Piece_Moved == 'P' or Piece_Moved == 'p'):
                        Current_Half_Move = 0
                    elif(Piece_Captured == "x"):
                        Current_Half_Move = 0
                    else:
                        Current_Half_Move += 1
                    current_fen = add_castling_rights(current_fen, castling_rights)
                    #current_fen = increment_fen_move_count(current_fen,move_count,Current_Half_Move)

                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = pgn_moves
                    #print(f" We are here 2 PGN from previous FEN to new FEN: {pgn}")
                    move_count += 1
                    fen_array[move_count-1] = current_fen
                    #send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    ChessBoard_array = ChessBoard_Current
                    
        #time.sleep(10)

finally:
    engine.quit()
