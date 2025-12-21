"""Consts."""
from .enums import Algorithm, FileDelivery

UPLOAD_DIR = "snapshots"
ALG = Algorithm.BF

"""PUZZLE data"""
SOURCE = "source/puzzle/"
NUM_ROWS = 3
NUM_COLS = 3

"""Piece data"""
PIECE_SOURCE = "source/piece/"

ASSETDIR = "assets"

ESP_SNAPSHOT = "input/snapshot.png"
ESP_HOST = "esp.slits.nl"

""" Discard bad matches """
TM_CUTOFF = 0.058
SFBF_CUTOFF = 5

"""Stream image from ESP or have ESP push it  """
IMG_SOURCE = FileDelivery.PUSH # PULL or PUSH

"""Server data"""
WS_PORT = 8765
HTTP_PORT = 8000
HTTP_HOST = "127.0.0.1"


