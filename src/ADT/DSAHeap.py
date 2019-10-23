"""
Referencing: The code in this file is similar to the code in DSAHeap.py,
submitted by Jakob Wyatt in prac 7. Differences include the sort method,
arbitraryRemove method, heap resizing, and additional unittests.
"""

import unittest
from typing import List, Tuple
from copy import copy
import numpy as np


class DSAHeapEntry:
    """
    This class is a convenience class for use within the DSAHeap class,
    and represents a single entry in the heap.
    """

    def __init__(self, priority: object, value: object):
        self._priority = priority
        self._value = value

    @property
    def priority(self) -> object:
        return self._priority
        
    @priority.setter
    def priority(self, p: object):
        self._priority = p

    @property
    def value(self) -> object:
        return self._value
        
    @value.setter
    def value(self, p: object):
        self._value = p


class DSAHeap:
    """
    This class implements a max-heap using an array.
    This gives O(nlog(n)) sort and O(log(n)) insert/remove.
    Resizing occurs automatically when the heap is too large.
    """

    def __init__(self, size: int = 100, *, resizeFactor=2.0):
        self._resizeFactor = resizeFactor
        self._heap = np.zeros(size, dtype=object)
        for i in range(len(self._heap)):
            self._heap[i] = DSAHeapEntry(None, None)
        self._count = 0

    def add(self, priority: object, value: object):
        if len(self) == len(self._heap):
            newHeap = np.zeros(int(len(self._heap) * self._resizeFactor), dtype=object)
            for i, x in enumerate(self._heap):
                newHeap[i] = x
            for i in range(len(self._heap), len(newHeap)):
                newHeap[i] = DSAHeapEntry(None, None)
            self._heap = newHeap
        self._heap[len(self)].priority = priority
        self._heap[len(self)].value = value
        self._trickleUp(len(self))
        self._count += 1

    def remove(self) -> Tuple[object, object]:
        if len(self) == 0:
            raise ValueError("Heap is empty.")
        priority = self._heap[0].priority
        value = self._heap[0].value
        self._count -= 1
        # Swap to conserve consistency of objects
        self._heap[0], self._heap[len(self)] = self._heap[len(self)], self._heap[0]
        self._trickleDown(0)
        return priority, value

    def removeArbitrary(self, item: object):
        # Interesting algorithm here.
        # First, the object to be removed must be found.
        i = 0
        found = False
        while i < len(self) and not found:
            found = self._heap[i].priority == item
            i += 1
        i -= 1
        if not found:
            raise ValueError("Element was not found.")
        # Next, swap it with the rightmost element.
        self._count -= 1
        self._heap[i], self._heap[len(self)] = self._heap[len(self)], self._heap[i]
        # Finally, trickle down this element
        self._trickleDown(i)

    def sort(self) -> List[Tuple[object, object]]:
        ret = np.zeros(len(self), dtype=object)
        tempHeap = copy(self)
        for i, _ in enumerate(ret):
            ret[i] = tempHeap.remove()
        return ret

    def _heapify(self):
        for i in reversed(range(len(self) // 2)):
            self._trickleDown(i)

    def _heapSort(self):
        self._heapify()
        size = len(self)
        for i in reversed(range(1, len(self))):
            self._heap[0], self._heap[i] = self._heap[i], self._heap[0]
            self._count -= 1
            self._trickleDown(0)
        self._count = size

    @staticmethod
    def heapSort(values: List[Tuple[object, object]]) -> List[Tuple[object, object]]:
        heap = DSAHeap(len(values))
        for i in range(len(values)):
            heap._heap[i].priority = values[i][0]
            heap._heap[i].value = values[i][1]
        heap._count = len(values)
        heap._heapSort()
        return [(x.priority, x.value) for x in heap._heap]

    def _trickleUp(self, index: int):
        parent = int((index - 1) / 2)
        if index > 0 and self._heap[parent].priority < self._heap[index].priority:
            self._heap[parent], self._heap[index] = self._heap[index], self._heap[parent]
            self._trickleUp(parent)

    def _trickleDown(self, index: int):
        left = index * 2 + 1
        right = left + 1
        # Choose the element to swap with
        swap = 0
        if left < len(self):
            swap = left
        if right < len(self) and self._heap[right].priority > self._heap[left].priority:
            swap = right
        # Perform the swap
        if swap != 0 and self._heap[swap].priority > self._heap[index].priority:
            self._heap[swap], self._heap[index] = self._heap[index], self._heap[swap]
            self._trickleDown(swap)

    def __len__(self):
        return self._count

    def __iter__(self):
        def iterate(heap):
            for i in range(len(heap)):
                yield heap._heap[i]
        return iterate(self)


class UnitTestDSAHeap(unittest.TestCase):
    """
    This class contains unittests for the DSAHeap class.
    """

    def testAddRemove(self):
        heap = DSAHeap(size=1)
        self.assertRaises(ValueError, heap.remove)
        heap.add(5, "five")
        heap.add(6, "six")
        heap.add(-1, "negone")
        heap.add(0, "zero")
        heap.add(1, "one")
        heap.add(-50, "neg50")
        heap.add(-51, "neg51")
        heap.add(50, "fifty")
        self.assertEqual(heap.remove(), (50, "fifty"))
        self.assertEqual(heap.remove(), (6, "six"))
        self.assertEqual(heap.remove(), (5, "five"))
        heap.add(100, "bignoi")
        heap.add(50, "fifty")
        heap.add(0, "zero")
        heap.add(-49, "neg49")
        heap.add(-51, "neg51")
        self.assertEqual(heap.remove(), (100, "bignoi"))
        self.assertEqual(heap.remove(), (50, "fifty"))
        self.assertEqual(heap.remove(), (1, "one"))
        self.assertEqual(heap.remove(), (0, "zero"))
        self.assertEqual(heap.remove(), (0, "zero"))
        self.assertEqual(heap.remove(), (-1, "negone"))
        self.assertEqual(heap.remove(), (-49, "neg49"))
        self.assertEqual(heap.remove(), (-50, "neg50"))
        self.assertEqual(heap.remove(), (-51, "neg51"))
        self.assertEqual(heap.remove(), (-51, "neg51"))

    def testHeapSort(self):
        with open("RandomNames7000.csv", "r") as f:
            student = [x.rstrip("\n").split(",") for x in f]
            for x1, x2 in zip(sorted(student), DSAHeap.heapSort(student)):
                self.assertEqual(x1[0], x2[0])

    def testHeapify(self):
        from functools import total_ordering
        @total_ordering
        class testPriority:
            def __init__(self, priority: int):
                self._priority = priority

            @property
            def priority(self):
                return self._priority

            @priority.setter
            def priority(self, priority: int):
                self._priority = priority

            def __eq__(self, other):
                return self.priority == other.priority

            def __lt__(self, other):
                return self.priority < other.priority

        heap = DSAHeap()
        vals = [testPriority(x) for x in range(5)]
        [heap.add(x, None) for x in vals]
        expected = [-3, -5, 50, 3, 1]
        for i, x in enumerate(expected):
            vals[i].priority = x
        heap._heapify()
        sortedHeap = heap.sort()
        for x, y in zip([50, 3, 1, -3, -5], sortedHeap):
            self.assertEqual(x, y[0].priority)

    def testRemoveArbitrary(self):
        heap = DSAHeap()
        heap.add(5, "five")
        heap.add(6, "six")
        heap.add(-1, "negone")
        heap.add(0, "zero")
        heap.add(1, "one")
        heap.add(-50, "neg50")
        heap.add(-51, "neg51")
        heap.add(50, "fifty")
        heap.removeArbitrary(-1)
        heap.removeArbitrary(50)
        heap.removeArbitrary(6)
        heap.removeArbitrary(-51)
        heap.removeArbitrary(-50)
        self.assertEqual(heap.remove(), (5, "five"))
        self.assertEqual(heap.remove(), (1, "one"))
        self.assertEqual(heap.remove(), (0, "zero"))

if __name__ == "__main__":
    unittest.main()
