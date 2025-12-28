"""Consts."""
from .enums import Algorithm

UPLOAD_DIR = "snapshots"
ALG = Algorithm.BF

"""PUZZLE data"""
SOURCE = "source/puzzle/"
NUM_ROWS = 3
NUM_COLS = 3

"""Piece data"""
PIECE_SOURCE = "source/piece/"

ASSETDIR = "assets"

""" Discard bad matches """
TM_CUTOFF = 0.058
SFBF_CUTOFF = 5

"""Server data"""
HTTP_PORT = 8000
HTTP_HOST = "127.0.0.1"


