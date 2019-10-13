import typing
import unittest
import pickle

class DSAListNode:
    def __init__(self, data: object, prev: 'DSAListNode', next: 'DSAListNode'):
        self._data = data
        self._prev = prev
        self._next = next

class DSALinkedList:
    def __init__(self):
        self._head = None
        self._tail = None

    def _insert(self, item: object, after: 'DSAListNode'):
        if after == None:
            # Insert at end
            node = DSAListNode(item, self._tail, None)
            self._tail = node
            if self.isEmpty():
                self._head = node
            else:
                node._prev._next = node
        else:
            node = DSAListNode(item, after._prev, after)
            after._prev = node
            if after is self._head:
                self._head = node
            else:
                node._prev._next = node
        
    def _remove(self, item: 'DSAListNode') -> object:
        if item is self._head:
            self._head = item._next
        else:
            item._prev._next = item._next

        if item is self._tail:
            self._tail = item._prev
        else:
            item._next._prev = item._prev
        return item._data
        
    def _find(self, item: object) -> 'DSAListNode':
        node = self._head
        while node != None and item != node._data:
            node = node._next
        return node

    def __iter__(self):
        def forward_gen(iter):
            while iter != None:
                yield iter._data
                iter = iter._next
        return forward_gen(self._head)

    def __reversed__(self):
        def reverse_gen(iter):
            while iter != None:
                yield iter._data
                iter = iter._prev        
        return reverse_gen(self._tail)

    def isEmpty(self) -> bool:
        return self._head == None

    def insertFirst(self, item: object):
        self._insert(item, self._head)
    
    def insertLast(self, item: object):
        self._insert(item, None)
    
    def insertBefore(self, item: object, before: object):
        self._insert(item, self._find(before))
    
    def peekFirst(self) -> object:
        return self._head._data

    def peekLast(self) -> object:
        return self._tail._data

    def removeFirst(self) -> object:
        return self._remove(self._head)

    def removeLast(self) -> object:
        return self._remove(self._tail)

    def remove(self, item: object) -> object:
        return self._remove(self._find(item))

    def find(self, item: object) -> bool:
        return self._find(item) != None

    def count(self) -> int:
        return sum(1 for _ in self)



class TestDSALinkedList(unittest.TestCase):
    def testConstructorIsEmpty(self):
        ll = DSALinkedList()
        self.assertTrue(ll.isEmpty)

    def testSimpleInsertAndPeek(self):
        ll = DSALinkedList()
        ll.insertFirst("abc")
        self.assertEqual(ll.peekFirst(), "abc")
        self.assertEqual(ll.peekLast(), "abc")
        ll.insertFirst("asd")
        self.assertEqual(ll.peekFirst(), "asd")
        self.assertEqual(ll.peekLast(), "abc")

    def testIter(self):
        ll = DSALinkedList()
        data = ["a", "b", "c", "d"]
        for x in data:
            ll.insertFirst(x)
        
        i = 0
        for x in reversed(ll):
            self.assertEqual(data[i], x)
            i += 1
        for i, elem in enumerate(ll):
            self.assertEqual(data[len(data) - i - 1], elem)

    def testFind(self):
        ll = DSALinkedList()
        ll.insertFirst("abc")
        ll.insertFirst("jkl")
        ll.insertFirst("xyz")
        self.assertTrue(ll.find("jkl"))
        self.assertTrue(ll.find("abc"))
        self.assertTrue(ll.find("xyz"))
        self.assertFalse(ll.find("jkq"))

    def testAdvInsertDelete(self):
        ll = DSALinkedList()
        ll.insertFirst("a")
        ll.insertBefore("b", "a")
        ll.insertLast("c")
        ll.insertBefore("d", "c")
        listState = ["b", "a", "d", "c"]
        for i, elem in enumerate(ll):
            self.assertEqual(listState[i], elem)
        ll.removeFirst()
        ll.remove("d")
        ll.removeLast()
        for i, elem in enumerate(ll):
            self.assertEqual("a", elem)

    def testSerialization(self):
        cucumber = DSALinkedList()
        cucumber.insertFirst("abc")
        cucumber.insertFirst("jkl")
        cucumber.insertFirst("xyz")
        with open("tmp", "wb") as f:
            pickle.dump(cucumber, f)
        with open("tmp", "rb") as f:
            gherkin = pickle.load(f)
        for x1, x2 in zip(gherkin, cucumber):
            self.assertEqual(x1, x2)

if __name__ == "__main__":
    unittest.main()