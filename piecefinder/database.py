"""SQLite."""
import json
import sqlite3

from .dataclass import Block, Piece, Puzzle, ResultDto


class Db:
    """SQLite."""
    cursor: sqlite3.Cursor

    def __init__(self):
        """Something about init."""
        con = sqlite3.connect("puzzledb.db")
        self.cursor = con.cursor()

    def get_puzzles(self) -> str:
        """Get puzzles from database."""
        self.cursor.execute("SELECT * FROM puzzles order by id")
        rows = self.cursor.fetchall()
        dbentries = [Puzzle(id=row[0], name=row[1], image=row[2]) for row in rows]
        return json.dumps([entry.__dict__ for entry in dbentries])

    def save_block(self,block: Block) -> int:
        """Save block to database."""
        self.cursor.execute("INSERT INTO blocks (x,y,width,height) VALUES (?,?,?,?)", (block.x, block.y, block.width, block.height))
        self.cursor.connection.commit()
        return self.cursor.lastrowid

    def get_block(self,id: int) -> Block:
        """Get block from database."""
        self.cursor.execute("SELECT x,y,width,height FROM blocks WHERE id = ?", (id,))
        row = self.cursor.fetchone()
        if row:
            return Block(x=row[0], y=row[1], width=row[2], height=row[3])
        return Block(x=0,y=0,width=0,height=0)

    def get_results(self,piece_id: int) -> ResultDto | None:
        """Get results from database."""
        self.cursor.execute("SELECT * FROM results WHERE piece_id = ?", (piece_id,))
        row = self.cursor.fetchone()
        if row:
            r = ResultDto(id=row[0], puzzle_id=row[1], piece_id=row[2], match=row[3])
            r.piece_position = self.get_block(row[0])
            return r
        return None

    def get_piece(self,piece_id: int) -> Piece:
        """Get piece from database."""
        self.cursor.execute("SELECT id,puzzle_id,filename FROM pieces WHERE id = ?", (piece_id,))
        row = self.cursor.fetchone()
        if row:
            return Piece(id=row[0], puzzle_id=row[1], filename=row[2])
        raise ValueError(f"Piece with id {piece_id} not found")

    def get_puzzle(self,puzzle_id: int) -> Puzzle:
        """Get puzzle from database."""
        self.cursor.execute("SELECT id,name,small,large FROM puzzles WHERE id = ?", (puzzle_id,))
        row = self.cursor.fetchone()
        if row:
            return Puzzle(id=row[0], name=row[1], small=row[2],large=row[3])
        raise ValueError(f"Puzzle with id {puzzle_id} not found")

    def save_puzzle(self,puzzle_name: str) -> None:
        """Save puzzle to database."""
        self.cursor.execute("INSERT INTO puzzles (name) VALUES (?)", (puzzle_name,))
        self.cursor.connection.commit()

    def save_results(self,data: ResultDto) -> int:
        """Save results to database."""
        block = data.piece_position
        self.cursor.execute("INSERT INTO blocks (x,y,width,height) VALUES (?,?,?,?)",
        (block.x, block.y, block.width, block.height))
        self.cursor.connection.commit()
        block_id = self.cursor.lastrowid
        data.piece_position = block_id
        print(f"Saved block with id {block_id}")
        print(f"Saving result for piece_id {data.piece_id} with match {data.match} and slice_count {data.slice_count}")
        self.cursor.execute("INSERT INTO results (puzzle_id, piece_id, match,slice_id,piece_position) VALUES (?,?,?,?,?)",
        (data.puzzle_id, data.piece_id, data.match, data.slice_count, block_id))
        self.cursor.connection.commit()
        return self.cursor.lastrowid

    def save_piece(self,piece: Piece) -> int:
        """Save piece to database."""

        self.cursor.execute("INSERT INTO pieces (puzzle_id, name, filename) VALUES (?,'blabla', ?)", (piece.puzzle_id, piece.filename))
        self.cursor.connection.commit()
        return self.cursor.lastrowid


