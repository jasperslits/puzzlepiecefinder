"""Dataclass definitions."""
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Block:
    """Result class."""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    score: float | None = None

class BlockDto:
    """Result class."""
    x: int = 0
    y: int  = 0
    width: int  = 0
    height: int = 0
    score: float = 0.0
    slice_index: int = 0

@dataclass
class ResultDto:
    """Result class."""
    id: int
    slice_count: int = 0
    puzzle_id: int = 0
    piece_id: int = 0
    match: int = 0
    piece_position: BlockDto | None = None


@dataclass
class Puzzle:
    """Puzzle class."""
    id: int
    name: str
    small: str
    large: str

@dataclass
class Piece:
    """Piece class."""
    id: int
    puzzle_id: int
    filename: uuid4().hex + ".png"



@dataclass
class APIResult:
    """Result class."""
    blocks: int
    foundblock: int
    piece: Block
    slice: Block
