class DirectedGraphNode():

    def __init__(self,
                 graph: DirectedGraph) -> None:
        self._graph: DirectedGraph = graph
    
    def adjacent_edges(self) -> list[DirectedGraphEdge]:
        return self._graph.node_adjacent_edges(self)

class DirectedGraphEdge():

    def __init__(self,
                 graph: DirectedGraph,
                 begin: DirectedGraphNode,
                 end: DirectedGraphNode) -> None:
        self._graph: DirectedGraph = graph
        self._begin_node: DirectedGraphNode = begin
        self._end_node: DirectedGraphNode = end

    def begin_node(self) -> DirectedGraphNode:
        return self._begin_node

    def end_node(self) -> DirectedGraphNode:
        return self._end_node

class DirectedGraph():

    def __init__(self) -> None:
        self._nodes: list[DirectedGraphNode] = []
        self._edges: list[DirectedGraphEdge] = []

    def add_node(self, node: DirectedGraphNode) -> DirectedGraphNode:
        if node not in self._nodes:
            self._nodes.append(node)
        return node

    def add_edge(self, edge: DirectedGraphEdge) -> DirectedGraphEdge:
        if not edge in self._edges:
            self._edges.append(edge)
        return edge

    def nodes(self) -> list[DirectedGraphNode]:
        return self._nodes

    def node_adjacent_edges(self, node: DirectedGraphNode) -> list[DirectedGraphEdge]:
        adjacent_edges: list[DirectedGraphEdge] = []
        for edge in self._edges:
            if edge.begin_node() == node or edge.end_node() == node:
                adjacent_edges.append(edge)
        return adjacent_edges
