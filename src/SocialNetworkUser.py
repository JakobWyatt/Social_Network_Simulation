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

    def follow(self, user: 'SocialNetworkUser') -> bool:
        if self == user:
            raise ValueError("User cannot follow themselves.")
        ret = False
        if not self._vertex.hasEdge(user.name()):
            ret = True
            self._vertex.addEdge(user._vertex)
        return ret

    def unfollow(self, user: 'SocialNetworkUser'):
        ret = False
        if self._vertex.hasEdge(user.name()):
            ret = True
            self._vertex.removeEdge(user.name())
        return ret

    def name(self) -> str:
        return self._vertex.label

    def __eq__(self, other: 'SocialNetworkUser') -> bool:
        return self._vertex is other._vertex

    def __lt__(self, other: 'SocialNetworkUser') -> bool:
        return len(self.followers()) < len(other.followers())
