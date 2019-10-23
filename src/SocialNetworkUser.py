from functools import total_ordering
from typing import List

from ADT.DSADirectedGraph import *
from ADT.DSALinkedList import *

@total_ordering
class SocialNetworkUser:
    """
    This class is a wrapper around a DSADirectedGraphVertex
    that has been created by the SocialNetwork class. As such, it does not store
    any data internally, and performs most functionality by calling corresponding
    functions within the DSADirectedGraphVertex class.

    The reason why this class was created was to create a wrapper around
    the DSADirectedGraphVertex class, using terms specific to social networks.
    This allows the DSADirectedGraph class to remain generic for future use.

    Another advantage is that this class can be returned from functions within
    the SocialNetwork class, which creates an external interface for user specific
    functionality. This means that the underlying implementation of a user may be changed
    without breaking any code that uses the SocialNetworkUser class.
    """

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
