import os

class Piece:
    file = ""
    name = ""

    def __init__(self,filename):
        self.file = filename
        p = os.path.basename(filename)
        piece_name,_ = os.path.splitext(p)
        self.name = piece_name
        print("Init")

    def cleanup(self):
        print("Hoi!")

    def removebg(self):
        print("Remove")