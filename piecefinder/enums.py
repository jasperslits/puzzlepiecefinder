"""Enums for PieceFinder."""
from enum import Enum


class Algorithm(Enum):
    """Algorithm types."""
    BF = "BF"
    TM = "TM"
    SF = "SF"

class FileDelivery(Enum):
    """File delivery methods."""
    PUSH = "PUSH"
    PULL = "PULL"
