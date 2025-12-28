"""Result class."""


from dataglasses import to_json_schema

from .database import Db
from .dataclass import ResultDto


class Result:
    """Result class."""

    data: ResultDto | None

    def save(self, data: ResultDto) -> int:
        """Save result to database."""
        return Db().save_results(data)

    def get_results(self,piece_id: int) -> ResultDto | None:
        """Get results from database."""
        return Db().get_results(piece_id)

    def get_results_json(self,piece_id: int) -> str:
        """Get data."""
        self.data = Db().get_results(piece_id)
        return to_json_schema(self.data)

    def __init__(self):
        """Something about init."""
        self.data = None


