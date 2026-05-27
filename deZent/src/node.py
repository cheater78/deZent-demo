
NodeID = int
class Node:

    def __init__(self, id: NodeID, known_peer: NodeID) -> None:
        self.id: NodeID = id
        self.prev: NodeID = 0
        self.next: NodeID = 0


