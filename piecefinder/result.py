"""Result class."""


from dataglasses import to_json_schema

from .const import NUM_COLS, NUM_ROWS
from .database import Db
from .dataclass import APIResult, Block, BlockDto, ResultDto


class Result:
    """Result class."""

    data: ResultDto | None

    def save(self) -> int:
        """Save result to database."""
        return Db().save_results(self.data)

    def to_json(self) -> str:
        """Get data."""
        return to_json_schema(self.data)

    def __init__(self,data: ResultDto):
        self.data = data


