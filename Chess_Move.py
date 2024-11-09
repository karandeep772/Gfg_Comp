import chess # type: ignore
import chess.engine #type: ignore
import chess.pgn #type: ignore
import time
import numpy as np
from pathlib import Path
#from chessboard_detector import get_chessboard
import requests
import sys
import json
from ChessBoard_Creation import ChessBoard_Creation
from Chess_MoveDetection import Chess_MoveDetection
from Fen_To_Array import fen_to_array
import cv2
from PIL import Image
import torch
#import serial
import time
# import pyttsx3
# from LightLeds import light_up_leds

# ser = serial.Serial('COM9', 115200)

#engine = pyttsx3.init()
model_ChessCorner = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5', 'custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp4\weights\best.pt', source='local')
model = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5', 'custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp3\weights\best.pt', source='local')
model_handdetection = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5','custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp5\weights\best.pt', source='local')
#model_handgesture = torch.hub.load(r'C:\Users\anmol\OneDrive\Desktop\karan\yolov5','custom', path=r'C:\Users\anmol\OneDrive\Desktop\HardWar\Models\exp6\weights\best.pt', source='local')

camera_index = 1  # Change if necessary
cap = cv2.VideoCapture(camera_index)

img_saved = False

# def announce_move(move):
#     engine.say(move)
#     engine.runAndWait()

fen_array = np.full(120, '', dtype=object)
#time.sleep(10)
ChessBoard_array = ChessBoard_Creation()

def get_chessboard(PathOFImage):
    # Loading the ChessBoards Corner Model

    # Setting the confidence Level
    model_ChessCorner.conf = 0.05

    # Define the source folder or image path
    image_path = PathOFImage

    result_ChessCorner = model_ChessCorner(image_path)
    result_ChessCorner.print()
    result_ChessCorner.save()

    corner_coordinates = []

    # Extract the x, y coordinates of the chessboard corners
    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()
    for detection in detections_ChessCorner:
        xmin, ymin, xmax, ymax, confidence, class_id = detection
        width = xmax - xmin
        height = ymax - ymin
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        corner_coordinates.append((center_x, center_y))
        #print(f"Chessboard corner detected at (x, y): ({center_x}, {center_y}) with confidence {confidence:.2f}")

    # Convert the list of coordinates to a NumPy array
    corner_coordinates_array = np.array(corner_coordinates)
    corner_coordinates_array[:] = corner_coordinates_array.astype(int)

    # Removing Duplicacy or Corners Which are very near(Sometimes more than 4 corners come)
    i = 0
    while i < len(corner_coordinates_array) - 1:
        j = i + 1
        while j < len(corner_coordinates_array):
            if abs(corner_coordinates_array[i][0] - corner_coordinates_array[j][0]) < 40 and abs(corner_coordinates_array[i][1] - corner_coordinates_array[j][1]) < 40:
                corner_coordinates_array = np.delete(corner_coordinates_array, j, axis=0)
            else:
                j += 1
        i += 1

    # Print the array with all stored coordinates
    #print("All detected corners' coordinates as NumPy array:\n\n", corner_coordinates_array)

    # Finding the minimum value of X
    minx = corner_coordinates_array[0][0]
    for i in range(1, len(corner_coordinates_array)):
        if minx > corner_coordinates_array[i][0]:
            minx = corner_coordinates_array[i][0]

    # Finding the second minimum value of X
    minx2 = float('inf')
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][0] != minx and corner_coordinates_array[i][0] < minx2:
            minx2 = corner_coordinates_array[i][0]

    # Handle case where there is no valid second minimum
    if minx2 == float('inf'):
        minx2 = None

    # Finding the maximum value of X
    maxx = corner_coordinates_array[0][0]
    for i in range(1, len(corner_coordinates_array)):
        if maxx < corner_coordinates_array[i][0]:
            maxx = corner_coordinates_array[i][0]

    # Finding the second maximum value of X
    maxx2 = float('-inf')  # Initialize with negative infinity
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][0] != maxx and corner_coordinates_array[i][0] > maxx2:
            maxx2 = corner_coordinates_array[i][0]

    # Handle case where there is no valid second maximum
    if maxx2 == float('-inf'):
        maxx2 = None


    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][0] == minx):
            y1 = corner_coordinates_array[i][1]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][0] == minx2):
            y2 = corner_coordinates_array[i][1]

    # Finding the minimum value of Y
    miny = corner_coordinates_array[0][1]
    for i in range(1, len(corner_coordinates_array)):
        if miny > corner_coordinates_array[i][1]:
            miny = corner_coordinates_array[i][1]

    # Finding the second minimum value of Y
    miny2 = float('inf')
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][1] != miny and corner_coordinates_array[i][1] < miny2:
            miny2 = corner_coordinates_array[i][1]

    #print("Minimum X value:", minx)
    #print("Second minimum X value:", minx2)

    # Finding the maximum value of Y
    maxy = corner_coordinates_array[0][1]
    for i in range(1, len(corner_coordinates_array)):
        if maxy < corner_coordinates_array[i][1]:  # Change > to <
            maxy = corner_coordinates_array[i][1]

    # Finding the second maximum value of Y
    maxy2 = float('-inf')  # Initialize with negative infinity for second max
    for i in range(len(corner_coordinates_array)):
        if corner_coordinates_array[i][1] != maxy and corner_coordinates_array[i][1] > maxy2:  # Change < to >
            maxy2 = corner_coordinates_array[i][1]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][1] == maxy):
            x1 = corner_coordinates_array[i][0]

    for i in range(len(corner_coordinates_array)):
        if(corner_coordinates_array[i][1] == maxy2):
            x2 = corner_coordinates_array[i][0]

    #print("Minimum Y value:", maxy)
    #print("Second minimum Y value:", maxy2)

    #Finding the Value of X and Y
    Y = abs(y2-y1)
    X = abs(x2-x1)
    x = X/8
    y = Y/8

    #print("\nValue of Y:",Y,"\nValue of X:",X, "\nValue of x:",x,"\nValue of y:",y,)

    ChessBoard = np.full((8, 8), '*', dtype=str)
    #print(ChessBoard)


    # Load the trained model (replace 'best.pt' with the path to your model if needed)
    # Set the confidence threshold (e.g., 0.5)
    model.conf = 0.65   # You can change this to adjust the confidence level

    # Inference on the image or a folder of images
    print(f"Using image path: {image_path}")

    # Uncomment below to use for chess piece detection
    results = model(image_path)

    results.print()
    results.save()

    # Optionally, you can access the results and bounding boxes
    detections_ChessCorner = result_ChessCorner.xyxy[0].cpu().numpy()

    # Extract chess piece details: (x, y), width, height, and piece name
    df = results.pandas().xyxy[0]

    bounding_boxes_with_names = []

    # Loop through each detected object
    for index, row in df.iterrows():
        xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        width = xmax - xmin
        height = ymax - ymin
        confidence = row['confidence']
        piece_name = row['name']  # Assuming the model's labels are chess piece names
        
        # Append the (xmin, ymin, width, height, piece_name) to the list
        bounding_boxes_with_names.append([xmin, ymin, width, height, piece_name])
        
        # Optional: print details for each detected piece
        #print(f"Detected {piece_name}: (x, y) = ({xmin}, {ymin}), width = {width}, height = {height}, confidence = {confidence:.2f}")

    # Convert the list to a NumPy array (without piece names since it's a string)
    bounding_boxes_array = np.array([item[:4] for item in bounding_boxes_with_names])

    # Print the NumPy array for bounding boxes
    #print(bounding_boxes_array)
    #print("Bounding Boxes (xmin, ymin, width, height):\n", bounding_boxes_array)

    # Print the piece names separately
    piece_names = [item[4] for item in bounding_boxes_with_names]
    #("Piece Names:\n", piece_names)

    for i in range(0,len(bounding_boxes_array)):
        #Finding Out the Column
        temph = bounding_boxes_array[i][1] + (bounding_boxes_array[i][3]/0.95)
        if temph<Y/2:
          if piece_names[i]=='black-rook':
              temph = temph - miny -20
          else:
              temph = temph - miny -5 #For right Half
        elif temph>Y/2:
            if piece_names[i]=='black-rook':
              temph = temph - miny -20
            else:
              temph = temph - miny
        print(temph)
        columno = int(temph/y)
        print(columno)
        columno = 7 - columno
        if columno<0:
            columno = abs(columno + 2 -1)
    
        #First Find out the row
        temp = bounding_boxes_array[i][0] + (bounding_boxes_array[i][2]/2)
        print("\n\n",temp)
        if (temp - minx) < X/4 and temph < Y/2: #First two right Quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx - 19 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1
        if (temp - minx) < X/4 and temph > Y/2: #First two left Quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx - 19 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) < X/2 and (temp - minx) > x/4 and temph <Y/2: #Third,Fourth row right quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx + 10 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) < X/2 and (temp - minx) > x/4 and temph > Y/2: #Third,Fourth row left quarter
            if piece_names[i]=='black-rook':
                temp = temp - minx - 20 - ((abs(minx2-minx)/8)*columno)/1.8
            elif piece_names[i]=='black-knight':
                temp = temp - minx - 24 - ((abs(minx2-minx)/8)*columno)/1.8
            else:
                temp = temp - minx + 10 - ((abs(minx2-minx)/8)*columno)/1.8            
            print(temp)
            rowno = int(temp/x)
            print(rowno,columno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            ChessBoard[rowno][columno] = temp1

        elif(temp - minx) > X/2 and (temp - minx) < 3*X/2 and temph < Y/2: #5,6 row right quarter
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            if piece_names[i]=='white-bishop':
              temp = maxx - temp - ((abs(maxx-maxx2)/8)*(columno))/1.8
            elif piece_names[i]=='white-rook':
              temp = maxx - temp - 5 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            elif piece_names[i]=='white-knight':
              temp = maxx - temp - 5 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            else:
                temp = maxx - temp + 7 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > X/2 and (temp - minx) < 3*X/2 and temph > Y/2: #5,6 row left quarter
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -1 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > 3*X/2 and temph < Y/2: #7,8 ROW RIGHT QUARTER
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -7 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1

        elif(temp - minx) > 3*X/2 and temph < Y/2: #7,8 ROW LEFT QUARTER
            F = maxx - temp
            print(F)
            G =  ((abs(maxx-maxx2)/8)*(columno))
            print(G)
            temp = maxx - temp -13 - ((abs(maxx-maxx2)/8)*(columno))/1.8
            print(temp)
            rowno = int(temp/x)
            print(rowno)
            if piece_names[i]=='black-rook':
                temp1 = 'r'
            elif piece_names[i]=='black-bishop':
                temp1 = 'b'
            elif piece_names[i]=='black-knight':
                temp1 = 'n'
            elif piece_names[i]=='black-pawn':
                temp1 = 'p'
            elif piece_names[i]=='black-queen':
                temp1 = 'q'
            elif piece_names[i]=='black-king':
                temp1 = 'k'
            elif piece_names[i]=='white-pawn':
                temp1 = 'P'
            elif piece_names[i]=='white-knight':
                temp1 = 'N'
            elif piece_names[i]=='white-bishop':
                temp1 = 'B'
            elif piece_names[i]=='white-king':
                temp1 = 'K'
            elif piece_names[i]=='white-queen':
                temp1 = 'Q'
            elif piece_names[i]=='white-rook':
                temp1 = 'R'        
            if(ChessBoard[7-rowno][columno] == '*'):
                ChessBoard[7-rowno][columno] = temp1  
            # else:
            #     ChessBoard[7-rowno][columno+1] = temp1

    #print(ChessBoard)
    return ChessBoard

def read_player_color():
    if len(sys.argv) < 2:
        print("Error: Player_Color argument is required.")
        sys.exit(1)

    try:
        player_color = int(sys.argv[1])  # Either 0 or 1
        if player_color not in [0, 1]:
            raise ValueError("Player_Color must be 0 or 1")
        return player_color
    except (IndexError, ValueError) as e:
        print(f"Error processing Player_Color argument: {e}")
        sys.exit(1)

Player_Color = read_player_color()

# Path to the Stockfish engine executable
engine_path = r"C:\Users\anmol\OneDrive\Desktop\HardWar\stockfish\stockfish.exe"

# Start the engine
engine = chess.engine.SimpleEngine.popen_uci(engine_path)
JC = 0
def fetch_chessboard(image_path):
    global JC
    if JC==0:
        image_path = r'C:\Users\anmol\OneDrive\Desktop\HardWar\Images1\\C13.jpg'
        JC += 1
    else:
        image_path = r'C:\Users\anmol\OneDrive\Desktop\HardWar\Images1\\C18.jpg'
    
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

def get_halfmove_count(fen):
    # FEN consists of 6 fields, and the half-move clock is the 5th one.
    fen_fields = fen.split()
    
    # The 5th field contains the half-move clock
    halfmove_clock = int(fen_fields[4])
    
    return halfmove_clock

def get_castling_rights(fen):
    # FEN consists of 6 fields, and the castling rights are the 4th one.
    fen_fields = fen.split()
    
    # The 4th field contains the castling rights
    castling_rights = fen_fields[2]
    
    return castling_rights

def handle_undo_request():
    global previous_fen, move_count, ChessBoard_array,current_fen,Player_Color,previous_black_fen,previous_white_fen,Current_Half_Move,castling_rights
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
        
        print("Inside undo function")
        if Player_Color == 1:
            previous_fen = fen_array[move_count-4]
            previous_white_fen = fen_array[move_count-4]
            previous_black_fen = fen_array[move_count-4]
        elif Player_Color == 0:
            previous_fen = fen_array[move_count-4]
            previous_white_fen = fen_array[move_count-4]
            previous_black_fen = fen_array[move_count-4]

        move_count -= 2
        current_fen = fen_to_send
        ChessBoard_array = fen_to_array(previous_fen)
        ChessBoard_Current = fen_to_array(current_fen)
        print(Current_Half_Move)
        previous_fen = current_fen
        Current_Half_Move = get_halfmove_count(previous_fen)
        ChessBoard_array = ChessBoard_Current

        if Player_Color == 1:
            previous_fen = update_fen_to_move(previous_fen, 'black')
            castling_rights = get_castling_rights(previous_fen)

        elif Player_Color == 0:
            previous_fen = update_fen_to_move(previous_fen, 'white')
            castling_rights = get_castling_rights(previous_fen)
        
        send_fen_to_javascript(fen_to_send,pgn,move_count)
        time.sleep(20)
        print(f"Undo: Reverted to FEN: {fen_to_send}")

def compare_piece_positions(fen1, fen2):
    # Extract only the piece placement part from the FEN strings (the first part)
    pieces_fen1 = fen1.split()[0]
    pieces_fen2 = fen2.split()[0]
    
    # Compare the piece placement parts
    if pieces_fen1 == pieces_fen2:
        return False
    else:
        return True
    

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
        ret, current_frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Check if the image is in portrait mode (height > width)
        # height, width, _ = current_frame.shape
        # # if height > width:
        #     # Rotate the image by 90 degrees to make it horizontal
        # current_frame = cv2.rotate(current_frame, cv2.ROTATE_90_CLOCKWISE)

        # Display the current frame
        #cv2.imshow("Camera", current_frame)

        # Save the image only once
        img_path = r'C:\Users\anmol\OneDrive\Desktop\HardWar\captured_image.png'

        # Capture the current frame
        cv2.imwrite(img_path, current_frame)
        print(f"Image saved at: {img_path}")
        img_saved = True

        # Load the YOLOv5 model for hand detection

        # # Set the confidence threshold
        # model_handgesture.conf = 0.1

        # # Perform inference on the image
        # results = model_handgesture(img_path)

        # # Print the results
        # results.print()

        # # Save the results
        # results.save()

        # # Check if a hand is detected
        # detected_objects = results.pandas().xyxy[0]  # Get the detection results as a DataFrame

        # if len(detected_objects) > 0:
        #     print("Hand detected! Capturing another image...")
        #     # Capture another image if hand is detected
        #     time.sleep(5)
        #     cv2.imwrite(img_path, current_frame)
        #     print(f"Second image saved at: {img_path}")
        # else:
        #     print("No hand detected.")

        model_handdetection.conf = 0.05

        # Perform inference on the image
        results = model_handdetection(img_path)

        # Print the results
        results.print()

        # Save the results
        results.save()

        # Check if a hand is detected
        detected_objects = results.pandas().xyxy[0]  # Get the detection results as a DataFrame

        if len(detected_objects) > 0:
            print("Hand detected! Capturing another image...")
            # Capture another image if hand is detected
            time.sleep(5)
            cv2.imwrite(img_path, current_frame)
            print(f"Second image saved at: {img_path}")
        else:
            print("No hand detected.")

        try:
            response = requests.get('http://localhost:3000/check_undo')
            if response.status_code == 200:
                undo_data = response.json()
                if undo_data.get('undo'):
                    handle_undo_request()
                    # Optionally reset the undo flag on the server
                    requests.post('http://localhost:3000/reset_undo')
            time.sleep(1)  # Check every second or adjust as needed
        except requests.RequestException as e:
            print(f"Error checking undo: {e}")
            time.sleep(5)  # Wait before retrying in case of an error
        except requests.RequestException as e:
            print(f"Error checking undo request: {e}")

        if Player_Color == 0:  #Player As White
            ChessBoard,ChessBoard_Current = fetch_chessboard(img_path)
            current_fen = array_to_fen(ChessBoard)

            if compare_piece_positions(current_fen, previous_fen) and previous_white_fen != current_fen:
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
                send_fen_to_javascript(current_fen, pgn, move_count)

                ChessBoard_array = ChessBoard_Current
                previous_fen = current_fen
                
                time.sleep(10)
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
                Led1 = (Sq[0][0] * 8) + Sq[0][1] + 1
                Led2 = (Sq[1][0] * 8) + Sq[1][1] + 1
                # light_up_leds([Led1, Led2])
                # time.sleep(10)
                # # Turn off all LEDs
                # light_up_leds([])


                pgn_moves = fen_to_pgn(previous_fen, current_fen)
                pgn = pgn_moves
                #announce_move(pgn_moves)
                #print(f"PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                send_fen_to_javascript(current_fen, pgn, move_count)
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
                #announce_move(pgn_moves)
                #print(f"In Player color1 move count 0 PGN from previous FEN to new FEN: {pgn}")
                move_count += 1
                fen_array[move_count-1] = current_fen
                send_fen_to_javascript(current_fen, pgn, move_count)
                previous_fen = update_fen_to_move(previous_fen,'black')
                previous_fen = current_fen
                time.sleep(5)
            else:
                ChessBoard,ChessBoard_Current = fetch_chessboard(img_path)
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
                    send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    previous_fen = update_fen_to_move(current_fen, 'white')
                    #print(current_fen)

                    time.sleep(10)
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
                    Led1 = (Sq[0][0] * 8) + Sq[0][1] + 1
                    Led2 = (Sq[1][0] * 8) + Sq[1][1] + 1
                    # light_up_leds([Led1, Led2])
                    # time.sleep(10)
                    # # Turn off all LEDs
                    # light_up_leds([])
                    pgn_moves = fen_to_pgn(previous_fen, current_fen)
                    pgn = pgn_moves
                    #announce_move(pgn_moves)
                    #print(f" We are here 2 PGN from previous FEN to new FEN: {pgn}")
                    move_count += 1
                    fen_array[move_count-1] = current_fen
                    send_fen_to_javascript(current_fen, pgn, move_count)
                    previous_fen = current_fen
                    ChessBoard_array = ChessBoard_Current
                    
        time.sleep(23)

finally:
    engine.quit()
    running = False
    cv2.destroyAllWindows()
    # ser.close()