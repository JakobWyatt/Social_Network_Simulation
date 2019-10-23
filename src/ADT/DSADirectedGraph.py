import unittest
import typing
import numpy as np

from ADT.DSAHashTable import DSAHashTable

class DSADirectedGraphVertex:
    """
    This class contains information about a vertex, including its
    label, data, and edges.
    This is a container class intended for use within the DSADirectedGraph
    class.
    """

    def __init__(self, label: object, value: object):
        self._label = label
        self._value = value
        self._successor = DSAHashTable()
        self._predecessor = DSAHashTable()

    @property
    def label(self) -> object:
        return self._label

    @property
    def value(self) -> object:
        return self._value

    @property
    def successor(self) -> 'DSAHashTable':
        return self._successor

    def addSuccessor(self, vertex: 'DSADirectedGraphVertex') -> None:
        self._successor.put(vertex.label, vertex)

    def removeSuccessor(self, vertex: 'DSADirectedGraphVertex') -> None:
        self._successor.remove(vertex.label)

    @property
    def predecessor(self) -> 'DSAHashTable':
        return self._predecessor

    def addPredecessor(self, vertex: 'DSADirectedGraphVertex') -> None:
        self._predecessor.put(vertex.label, vertex)

    def removePredecessor(self, vertex: 'DSADirectedGraphVertex') -> None:
        self._predecessor.remove(vertex.label)

    def addEdge(self, vertex: 'DSADirectedGraphVertex') -> None:
        self.addSuccessor(vertex)
        vertex.addPredecessor(self)

    def hasEdge(self, label: str) -> bool:
        return self.successor.hasKey(label)

    def removeEdge(self, label: str) -> None:
        vertex = self.successor.get(label)
        self.removeSuccessor(vertex)
        vertex.removePredecessor(self)

    def __str__(self) -> str:
        return ("{label},{value}:{adj}"
                .format(label=self.label, value=self.value,
                        adj=" ".join([k for k, v in self.successor])))

    def gv(self) -> str:
        return "".join([f"\"{self.label}\" -> \"{k}\"\n" for k, v in self.successor])

    def __eq__(self, other: 'DSADirectedGraphVertex') -> bool:
        return self.label == other.label


class DSADirectedGraph:
    """
    This class is an ADT of a directed graph, and contains functionality
    to add/remove verticies and edges from the graph.

    It is currently implemented using the DSAHashTable data structure,
    however it has been implemented using a DSALinkedList in the past.
    """

    def __init__(self):
        self._verticies = DSAHashTable()

    def addVertex(self, label: object, value: object) -> None:
        """
        Does not check for duplicates.
        """
        self._verticies.put(label, DSADirectedGraphVertex(label, value))

    def removeVertex(self, label: object) -> None:
        vertex = self.getVertex(label)
        for _, v in vertex.predecessor:
            v.removeSuccessor(vertex)
        for _, v in vertex.successor:
            v.removePredecessor(vertex)
        self._verticies.remove(vertex.label)

    def addEdge(self, label1: object, label2: object) -> None:
        self.getVertex(label1).addEdge(self.getVertex(label2))

    def hasEdge(self, label1: object, label2: object) -> bool:
        return self.getVertex(label1).hasEdge(label2)

    def removeEdge(self, label1: object, label2: object) -> None:
        self.getVertex(label1).removeEdge(label2)

    def hasVertex(self, label: object) -> bool:
        return self._verticies.hasKey(label)

    def getVertexCount(self) -> int:
        return len(self._verticies)

    def getEdgeCount(self) -> int:
        return sum(len(v.successor) for _, v in self._verticies)

    def __iter__(self):
        return self._verticies.__iter__()

    def getVertex(self, label: object) -> 'DSADirectedGraphVertex':
        return self._verticies.get(label)

    def getSuccessor(self, label: object) -> 'DSAHashTable':
        return self.getVertex(label).successor

    def getPredecessor(self, label: object) -> 'DSAHashTable':
        return self.getVertex(label).predecessor

    def isSuccessor(self, label1: object, label2: object) -> bool:
        return self.getVertex(label1).successor.hasKey(label2)

    def displayAsList(self) -> str:
        return "".join(f"{v}\n" for _, v in self._verticies)

    def displayAsMatrix(self) -> str:
        label = [k for k, _ in self._verticies]
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

    def displayExploded(self) -> str:
        first = "".join([f"{k}\n" for k, _ in self._verticies])
        second = ""
        for k, v in self._verticies:
            second = second + "".join([f"{lf}:{k}\n" for lf, _ in v.successor])
        return first + second

    def adjacencyMatrix(self):
        count = self.getVertexCount()
        mat = np.zeros([count, count], dtype=int)
        for i, v in enumerate(self._verticies):
            for j, l in enumerate(self._verticies):
                mat[i][j] = 1 if v[1].successor.hasKey(l[0]) else 0
        return mat

    def display(self) -> str:
        return "digraph {\nrankdir=BT\nconcentrate=true\n" + "".join([v.gv() for _, v in self._verticies]) + "}\n"

    def render(self, *, type='svg', id=''):
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
            print("Graphviz not installed. Falling back on adjacency list display.")
            print(self.displayAsList())
        else:
            with NamedTemporaryFile(delete=False, suffix=f'{id}.{type}') as f:
                # Render the graph.
                run(["dot", f"-T{type}", "-o", f.name], input=self.display().encode())
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


class UnitTestDSADirectedGraph(unittest.TestCase):
    """
    This class contains unittests for the DSADirectedGraph class.
    """

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
        self.assertTrue(graph.isSuccessor("hello", "world"))
        self.assertFalse(graph.isSuccessor("yeah", "world"))
        self.assertFalse(graph.isSuccessor("world", "hello"))
        graph.addEdge("hello", "yeah")
        graph.addEdge("world", "hello")
        for x1, x2 in zip(graph.getSuccessor("hello"), ["yeah", "world"]):
            self.assertEqual(x1[0], x2)
        for x1, x2 in zip(graph.getPredecessor("hello"), ["world"]):
            self.assertEqual(x1[0], x2)
    
    def testRemoval(self):
        graph = DSADirectedGraph()
        graph.addVertex("a", None)
        graph.addVertex("b", None)
        graph.addVertex("c", None)
        graph.addEdge("a", "b")
        graph.addEdge("b", "a")
        graph.addEdge("c", "b")
        graph.addEdge("c", "a")
        self.assertTrue(graph.isSuccessor("a", "b"))
        self.assertTrue(graph.isSuccessor("b", "a"))
        self.assertTrue(graph.isSuccessor("c", "b"))
        self.assertTrue(graph.isSuccessor("c", "a"))
        self.assertFalse(graph.isSuccessor("a", "c"))
        self.assertFalse(graph.isSuccessor("b", "c"))
        graph.removeEdge("b", "a")
        self.assertTrue(graph.isSuccessor("a", "b"))
        self.assertFalse(graph.isSuccessor("b", "a"))
        graph.addEdge("a", "b")
        graph.removeVertex("b")
        self.assertFalse(graph.isSuccessor("a", "b"))
        self.assertFalse(graph.isSuccessor("c", "b"))
        self.assertTrue(graph.isSuccessor("c", "a"))
        self.assertFalse(graph.isSuccessor("a", "c"))

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


if __name__ == "__main__":
    unittest.main()
