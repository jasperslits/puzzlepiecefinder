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
    score: float = 0.0

@dataclass
class HistoryDto:
    """History class."""
    id: int
    puzzle_name: str
    piece_id: int
    date: str
    match: int

@dataclass
class BlockDto:
    """Result class."""
    id: int = 0
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
    piece_position: BlockDto = None
    slice_position: BlockDto = None

@dataclass
class PuzzleDto:
    """Puzzle class."""
    id: int
    name: str
    small: str
    large: str

@dataclass
class PieceDto:
    """Piece class."""
    id: int = 0
    puzzle_id: int = 0
    filename: str = uuid4().hex + ".png"

@dataclass
class SliceDto:
    """Slice class."""
    id: int = 0
    puzzle_id: int = 0
    slice_id: int = 0
    position: BlockDto | None = None


@dataclass
class APIResult:
    """Result class."""
    blocks: int
    foundblock: int
    piece: Block
    slice: Block
