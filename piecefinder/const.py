"""Consts."""
from enums import Algorithm

UPLOAD_DIR = "snapshots"
ALG = Algorithm.TM

"""PUZZLE data"""
PUZZLE_FILE = "source/puzzle/klas.jpg"
SOURCE = "source/puzzle/"
NUM_ROWS = 3
NUM_COLS = 3

"""Piece data"""
PIECE_SOURCE = "source/piece/"

PIECE_FINAL = 'source/piece/final.png'

ESP_SNAPSHOT = "input/snapshot.jpg"
ESP_HOST = "esp.slits.nl"

""" Discard bad matches """
TM_CUTOFF = 0.058
SFBF_CUTOFF = 5

"""Stream image from ESP or have ESP push it  """
IMG_SOURCE = "PULL" # PULL or PUSH

"""Server data"""
WS_PORT = 8765
HTTP_PORT = 8000
HTTP_HOST = "0.0.0.0"


