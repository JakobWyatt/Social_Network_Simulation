from functools import total_ordering
from typing import List

from ADT.DSADirectedGraph import *
from ADT.DSALinkedList import *

@total_ordering
class SocialNetworkUser:
    def __init__(self, vertex: DSADirectedGraphVertex):
        self._vertex = vertex

    @property
    def posts(self) -> DSALinkedList:
        return self._vertex.value

    def addPost(self, post: 'SocialNetworkPost'):
        self._vertex.value.insertFirst(post)

    def followers(self) -> List['SocialNetworkUser']:
        return [SocialNetworkUser(v) for _, v in self._vertex.predecessor]

    def following(self) -> List['SocialNetworkUser']:
        return [SocialNetworkUser(v) for _, v in self._vertex.successor]

    def name(self) -> str:
        return self._vertex.label

    def __eq__(self, other):
        return self._vertex is other._vertex

    def __lt__(self, other):
        return len(self.followers()) < len(other.followers())
