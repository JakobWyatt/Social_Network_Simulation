import unittest
import typing
import numpy as np

from ADT.linkedLists import DSALinkedList
from ADT.DSAListQueue import DSAListQueue
from ADT.DSAListStack import DSAListStack


class DSADirectedGraphVertex:
    def __init__(self, label: object, value: object):
        self._label = label
        self._value = value
        self._adjacent = DSALinkedList()
        self._visited = False

    @property
    def label(self) -> object:
        return self._label

    @property
    def value(self) -> object:
        return self._value

    @property
    def adjacent(self) -> 'DSALinkedList':
        return self._adjacent

    def addEdge(self, vertex: 'DSADirectedGraphVertex') -> None:
        self._adjacent.insertFirst(vertex)

    @property
    def visited(self) -> bool:
        return self._visited

    @visited.setter
    def visited(self, visited: bool) -> None:
        self._visited = bool(visited)

    def __str__(self) -> str:
        return ("{label},{value}:{adj}"
                .format(label=self.label, value=self.value,
                        adj=" ".join([x.label for x in self.adjacent])))

    def gv(self) -> str:
        return "".join([f"{self.label} -> {x.label}\n" for x in self.adjacent])

    def __eq__(self, other: 'DSADirectedGraphVertex') -> bool:
        return self.label == other.label


class DSADirectedGraph:
    def __init__(self):
        self._verticies = DSALinkedList()

    def addVertex(self, label: object, value: object) -> None:
        """
        Does not check for duplicates.
        """
        self._verticies.insertFirst(DSADirectedGraphVertex(label, value))

    def addEdge(self, label1: object, label2: object) -> None:
        """
        Assumes that the nodes already exist.
        """
        vertex1 = self.getVertex(label1)
        vertex2 = self.getVertex(label2)
        vertex1.addEdge(vertex2)

    def hasVertex(self, label: object) -> bool:
        return self._verticies.find(DSADirectedGraphVertex(label, None))

    def getVertexCount(self) -> int:
        return self._verticies.count()

    def getEdgeCount(self) -> int:
        return sum(x.adjacent.count() for x in self._verticies)

    def getVertex(self, label: object) -> 'DSADirectedGraphVertex':
        # Use list internals for efficiency
        return self._verticies._find(DSADirectedGraphVertex(label, None))._data

    def getAdjacent(self, label: object) -> 'DSALinkedList':
        return self.getVertex(label).adjacent

    def isAdjacent(self, label1: object, label2: object) -> bool:
        return self.getVertex(label1).adjacent.find(DSADirectedGraphVertex(label2, None))

    def displayAsList(self) -> str:
        return "".join(f"{x}\n" for x in self._verticies)

    def displayAsMatrix(self) -> str:
        label = [str(x.label) for x in self._verticies]
        colWidth = len(max(label, key=lambda x: len(x))) + 1
        # Pad initial row of labels
        matStr = ' ' * colWidth
        matStr += "".join([x + " " * (colWidth - len(x)) for x in label])
        matStr += "\n"
        adjMat = self.adjacencyMatrix()
        for i, l in enumerate(label):
            matStr += l + " " * (colWidth - len(l))
            matStr += (" " * (colWidth - 1)).join([str(x) for x in adjMat[i].flat])
            matStr += "\n"
        return matStr

    def adjacencyMatrix(self):
        count = self.getVertexCount()
        mat = np.zeros([count, count], dtype=int)
        for i, v in enumerate(self._verticies):
            for j, l in enumerate(self._verticies):
                mat[i][j] = 1 if v.adjacent.find(l) else 0
        return mat

    def display(self) -> str:
        return "digraph {\n" + "".join([x.gv() for x in self._verticies]) + "}\n"

    @staticmethod
    def render(gv: str, *, type='svg', id=''):
        """
        Renders a graphviz DOT file.
        Prints the render result to a temporary output file.
        Opens this file using the default program assigned
        to the given extension.
        """
        from subprocess import run
        from shutil import which
        from tempfile import NamedTemporaryFile

        if which("dot") is None:
            raise RuntimeError("Rendering DOT files requires "
                               "graphviz to be installed.")
        else:
            with NamedTemporaryFile(delete=False, suffix=f'{id}.{type}') as f:
                # Render the graph.
                run(["dot", f"-T{type}", "-o", f.name], input=gv.encode())
                # Attempt to display the graph.
                if which("xdg-open") is not None:
                    run(["xdg-open", f.name])
                elif which("open") is not None:
                    run(["open", f.name])
                else:
                    print("Could not open the rendered image. "
                          f"File written to {f.name}")

    @staticmethod
    def readGraphFile(filename: str) -> 'DSADirectedGraph':
        graph = DSADirectedGraph()
        with open(filename, "r") as f:
            for l in f:
                l1, l2 = l.rstrip("\n").split(" ")
                if not graph.hasVertex(l1):
                    graph.addVertex(l1, None)
                if not graph.hasVertex(l2):
                    graph.addVertex(l2, None)
                graph.addEdge(l1, l2)
        return graph

    def depthFirstSearch(self) -> 'DSADirectedGraph':
        # Mark nodes as new
        tree = DSADirectedGraph()
        stack = DSAListStack()
        for v in self._verticies:
            v.visited = False

        # Set up first node
        if self._verticies._head is not None:
            head = self._verticies.peekFirst()
            head.visited = True
            tree.addVertex(head.label, head.value)
            stack.push(head)
        
        # Perform DFS
        while not stack.isEmpty():
            node = next((x for x in stack.top().adjacent if not x.visited), None)
            if node is None:
                stack.pop()
            else:
                node.visited = True
                tree.addVertex(node.label, node.value)
                tree.addEdge(stack.top().label, node.label)
                stack.push(node)
        return tree

    def breadthFirstSearch(self) -> 'DSADirectedGraph':
        tree = DSADirectedGraph()
        queue = DSAListQueue()
        for v in self._verticies:
            v.visited = False
        
        if self._verticies._head is not None:
            head = self._verticies.peekFirst()
            head.visited = True
            tree.addVertex(head.label, head.value)
            queue.enqueue(head)
        
        while not queue.isEmpty():
            centre = queue.dequeue()
            for v in centre.adjacent:
                if not v.visited:
                    queue.enqueue(v)
                    tree.addVertex(v.label, v.value)
                    tree.addEdge(centre.label, v.label)
                    v.visited = True
        return tree


class TestDSADirectedGraph(unittest.TestCase):
    def testAddVertex(self):
        graph = DSADirectedGraph()
        self.assertFalse(graph.hasVertex("hello"))
        graph.addVertex("hello", "world")
        self.assertTrue(graph.hasVertex("hello"))
        self.assertFalse(graph.hasVertex("world"))
        graph.addVertex("world", "hello")
        self.assertTrue(graph.hasVertex("world"))

    def testVertexCount(self):
        graph = DSADirectedGraph()
        self.assertEqual(0, graph.getVertexCount())
        graph.addVertex("hello", "world")
        self.assertEqual(1, graph.getVertexCount())
        graph.addVertex("world", "hello")
        self.assertEqual(2, graph.getVertexCount())

    def testAdjacentEdge(self):
        graph = DSADirectedGraph()
        graph.addVertex("hello", "world")
        graph.addVertex("world", "hello")
        graph.addVertex("yeah", "boi")
        graph.addEdge("hello", "world")
        self.assertTrue(graph.isAdjacent("hello", "world"))
        self.assertFalse(graph.isAdjacent("yeah", "world"))
        self.assertFalse(graph.isAdjacent("world", "hello"))
        graph.addEdge("hello", "yeah")
        for x1, x2 in zip(graph.getAdjacent("hello"), ["yeah", "world"]):
            self.assertEqual(x1.label, x2)

    def testEdgeCount(self):
        graph = DSADirectedGraph()
        self.assertEqual(graph.getEdgeCount(), 0)
        graph.addVertex("hello", "world")
        graph.addVertex("world", "hello")
        graph.addVertex("yeah", "boi")
        self.assertEqual(graph.getEdgeCount(), 0)
        graph.addEdge("hello", "world")
        self.assertEqual(graph.getEdgeCount(), 1)
        graph.addEdge("yeah", "hello")
        self.assertEqual(graph.getEdgeCount(), 2)
        graph.addEdge("yeah", "world")
        self.assertEqual(graph.getEdgeCount(), 3)

    def testListDisplay(self):
        graph = DSADirectedGraph()
        graph.addVertex("hello", "world")
        graph.addVertex("world", "hello")
        graph.addVertex("yeah", "boi")

        graph.addEdge("hello", "world")
        graph.addEdge("yeah", "hello")
        graph.addEdge("yeah", "world")

        self.assertEqual(graph.displayAsList(),
                        ("yeah,boi:world hello\n"
                         "world,hello:\n"
                         "hello,world:world\n"))

    def testMatrixDisplay(self):
        graph = DSADirectedGraph()
        graph.addVertex("hello", "world")
        graph.addVertex("world", "hello")
        graph.addVertex("yeah", "boi")

        graph.addEdge("hello", "world")
        graph.addEdge("yeah", "hello")
        graph.addEdge("yeah", "world")

        self.assertEqual(graph.displayAsMatrix(),
                        ("      yeah  world hello \n"
                         "yeah  0     1     1\n"
                         "world 0     0     0\n"
                         "hello 0     1     0\n"))

    def testDisplay(self):
        graph = DSADirectedGraph()
        graph.addVertex("hello", "world")
        graph.addVertex("world", "hello")
        graph.addVertex("yeah", "boi")

        graph.addEdge("hello", "world")
        graph.addEdge("yeah", "hello")
        graph.addEdge("yeah", "world")

        self.assertEqual(graph.display(),
                        ("digraph {\n"
                         "yeah -> world\n"
                         "yeah -> hello\n"
                         "hello -> world\n"
                         "}\n"))

    def testReadGraphFile(self):
        readGraph = DSADirectedGraph.readGraphFile("prac6_1.al")
        graph = DSADirectedGraph()
        graph.addVertex("A", None)
        graph.addVertex("B", None)
        graph.addVertex("E", None)
        graph.addVertex("D", None)
        graph.addVertex("C", None)
        graph.addVertex("F", None)
        graph.addVertex("G", None)
        graph.addEdge("A", "B")
        graph.addEdge("A", "E")
        graph.addEdge("A", "D")
        graph.addEdge("A", "C")
        graph.addEdge("B", "E")
        graph.addEdge("C", "D")
        graph.addEdge("D", "F")
        graph.addEdge("E", "F")
        graph.addEdge("E", "G")
        graph.addEdge("F", "G")
        self.assertEqual(graph.displayAsMatrix(), readGraph.displayAsMatrix())

    def testBFSandDFS(self):
        graph1 = DSADirectedGraph.readGraphFile("3a.al")
        graph2 = DSADirectedGraph.readGraphFile("3b.al")

        bfs1Str = ("G,None:\n"
                   "F,None:\n"
                   "E,None:G\n"
                   "D,None:F\n"
                   "C,None:\n"
                   "B,None:\n"
                   "A,None:E D C B\n")
        self.assertEqual(graph1.breadthFirstSearch().displayAsList(), bfs1Str)

        dfs1Str = ("D,None:\n"
                   "C,None:D\n"
                   "G,None:\n"
                   "F,None:G\n"
                   "E,None:F\n"
                   "B,None:E\n"
                   "A,None:C B\n")
        self.assertEqual(graph1.depthFirstSearch().displayAsList(), dfs1Str)

if __name__ == "__main__":
    unittest.main()
