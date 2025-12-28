"""SQLite."""
import json
import sqlite3

from .const import NUM_COLS, NUM_ROWS
from .dataclass import BlockDto, HistoryDto, PieceDto, PuzzleDto, ResultDto, SliceDto


class Db:
    """SQLite."""
    cursor: sqlite3.Cursor

    def __init__(self):
        """Something about init."""
        con = sqlite3.connect("puzzledb.db")
        self.cursor = con.cursor()

    def get_slice(self,puzzle_id: int, slice_id: int) -> BlockDto:
        """Get slice from database."""
        self.cursor.execute("SELECT id,puzzle_id,slice_id,x,y,width,height FROM slices WHERE puzzle_id = ? AND slice_id = ?", (puzzle_id, slice_id))
        row = self.cursor.fetchone()
        if row:
            return BlockDto(id=row[0],  x=row[3], y=row[4], width=row[5], height=row[6], score=0.0)

        print(f"Slice not found for puzzle_id {puzzle_id} and slice_id {slice_id}")
        return None

    def check_slice(self,puzzle_id: int) -> bool:
        """Check if slices exist for puzzle."""
        self.cursor.execute("SELECT COUNT(*) FROM slices WHERE puzzle_id = ?", (puzzle_id,))
        row = self.cursor.fetchone()
        if row and row[0] > 0:
            return True
        return False

    def save_slice(self,slice: SliceDto) -> int:
        """Save slice to database."""
        self.cursor.execute("INSERT INTO slices (puzzle_id,slice_id,x,y,width,height) VALUES (?,?,?,?,?,?)",
        (slice.puzzle_id, slice.slice_id,slice.position.x, slice.position.y, slice.position.width, slice.position.height))
        self.cursor.connection.commit()
        return self.cursor.lastrowid

    def get_histories_json(self) -> str:
        """Get histories from database."""
        self.cursor.execute("SELECT id,puzzle_id,piece_id,match FROM results order by id desc limit 10")
        rows = self.cursor.fetchall()
        dbentries = [HistoryDto(id=row[0], puzzle_name=row[1],piece_id=row[2], match=row[3]) for row in rows]
        return json.dumps([entry.__dict__ for entry in dbentries])


    def get_puzzles_json(self) -> str:
        """Get puzzles from database."""
        self.cursor.execute("SELECT id,name,large,small FROM puzzles order by id")
        rows = self.cursor.fetchall()
        dbentries = [PuzzleDto(id=row[0], name=row[1], large=row[2],small=row[3]) for row in rows]
        return json.dumps([entry.__dict__ for entry in dbentries])

    def save_block(self,block: BlockDto) -> int:
        """Save block to database."""
        self.cursor.execute("INSERT INTO blocks (x,y,width,height,score) VALUES (?,?,?,?,?)", (block.x, block.y, block.width, block.height, block.score))
        self.cursor.connection.commit()
        return self.cursor.lastrowid

    def get_block(self,id: int) -> BlockDto:
        """Get block from database."""
        self.cursor.execute("SELECT id,x,y,width,height,score FROM blocks WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        if row:
            return BlockDto(id=row[0], x=row[1], y=row[2], width=row[3], height=row[4], score=row[5])
        return BlockDto()

    def get_results(self,piece_id: int) -> ResultDto | None:
        """Get results from database."""
        self.cursor.execute("SELECT id,puzzle_id,piece_id,match FROM results WHERE piece_id = ?", (piece_id,))
        row = self.cursor.fetchone()
        if row:
            r = ResultDto(id=row[0], puzzle_id=row[1], piece_id=row[2], match=row[3],slice_count=NUM_COLS * NUM_ROWS)
            r.piece_position = self.get_block(r.id)
            r.slice_position = self.get_slice(r.puzzle_id, r.match)
            return r
        return None

    def get_piece(self,piece_id: int) -> PieceDto | None:
        """Get piece from database."""
        self.cursor.execute("SELECT id,puzzle_id,filename FROM pieces WHERE id = ?", (piece_id,))
        row = self.cursor.fetchone()
        if row:
            return PieceDto(id=row[0], puzzle_id=row[1], filename=row[2])
        return None

    def get_puzzle(self,puzzle_id: int) -> PuzzleDto:
        """Get puzzle from database."""
        self.cursor.execute("SELECT id,name,small,large FROM puzzles WHERE id = ?", (puzzle_id,))
        row = self.cursor.fetchone()
        if row:
            return PuzzleDto(id=row[0], name=row[1], small=row[2],large=row[3])
        raise ValueError(f"Puzzle with id {puzzle_id} not found")

    def save_puzzle(self,puzzle_name: str) -> None:
        """Save puzzle to database."""
        self.cursor.execute("INSERT INTO puzzles (name) VALUES (?)", (puzzle_name,))
        self.cursor.connection.commit()

    def save_results(self,data: ResultDto) -> int:
        """Save results to database."""
        block = data.piece_position
        block_id =  self.save_block(block)
        data.piece_position = block_id
        print(f"Saved block with id {block_id}")
        print(f"Saving result for piece_id {data.piece_id} with match {data.match} and slice_count {data.slice_count}")
        self.cursor.execute("INSERT INTO results (puzzle_id, piece_id, match,slice_id,piece_position) VALUES (?,?,?,?,?)",
        (data.puzzle_id, data.piece_id, data.match, data.slice_count, block_id))
        self.cursor.connection.commit()
        return self.cursor.lastrowid

    def save_piece(self,piece: PieceDto) -> int:
        """Save piece to database."""

        self.cursor.execute("INSERT INTO pieces (puzzle_id, name, filename) VALUES (?,'blabla', ?)", (piece.puzzle_id, piece.filename))
        self.cursor.connection.commit()
        return self.cursor.lastrowid


