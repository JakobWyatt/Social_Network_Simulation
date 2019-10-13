from typing import List
from functools import total_ordering

from ADT.DSADirectedGraph import DSADirectedGraph, DSADirectedGraphVertex
from ADT.DSALinkedList import DSALinkedList, DSAListNode
from ADT.DSAHeap import DSAHeap
from ADT.DSAOrderedList import DSAOrderedList

class SocialNetwork:
    def __init__(self, *, probLike=-1.0, probFollow=-1.0):
        if probLike == -1.0 and probFollow == -1.0:
            self._probLike = -1.0
            self._probFollow = -1.0
        else:
            self.probLike = probLike
            self.probFollow = probFollow
        self._network = DSADirectedGraph()
        # In order of posting
        self._posts = DSALinkedList()
        # In order of likes - O(n) insertion, O(n) update (low), O(n) retrival
        self._postLikes = DSAOrderedList()
        self._currentPost = None

    @property
    def probLike(self) -> float:
        return self._probLike

    @probLike.setter
    def probLike(self, prob: float):
        SocialNetwork._checkProb(prob)
        self.probLike = prob

    @property
    def probFollow(self) -> float:
        return self._probFollow

    @probFollow.setter
    def probFollow(self, prob: float):
        SocialNetwork._checkProb(prob)
        self.probFollow = prob

    def loadNetwork(self, file):
        ...

    def follow(self, follower: str, followed: str):
        self._network.addEdge(follower, followed)

    def unfollow(self, follower: str, followed: str):
        ...

    def like(self, user: str, postId: int):
        ...

    def unlike(self, user: str, postId: int):
        ...

    def addUser(self, user: str):
        self._network.addVertex(user, None)

    def removeUser(self, user: str):
        ...

    def findUser(self, user: str) -> 'SocialNetworkUser':
        ...

    def display(self):
        self._network.render()

    def update(self):
        ...

    def save(self) -> str:
        ...

    def addPost(self, user: str, content: str):
        self._posts.insertFirst(SocialNetworkPost(user, content))

    def done(self) -> bool:
        return self._posts.count() == 0 or self._posts.peekFirst().done()

    # Statistics methods

    def simstate(self) -> str:
        """Outputs all statistics required for the simulation timestep.

        Returns:
            Network representation, most recent post representation,
            and optional statistics.
        """
        return f"{self.save()}\n{self._posts.peekFirst().save()}\n{self.optionalStats()}"

    def optionalStats(self) -> str:
        """Outputs optional statistics about the network.
        """
        return ""

    def popularPosts(self) -> List['SocialNetworkPost']:
        ...

    def popularUsers(self) -> List['SocialNetworkUser']:
        ...

    # Private methods

    @staticmethod
    def _checkProb(prob):
        if prob < 0 or prob > 1:
            raise ValueError("Probabilities must be in the range [0, 1]")

    def _canUpdate(self) -> bool:
        return (self._probFollow != -1.0
                and self._probLike != -1.0
                and self._network.getVertexCount() != 0
                and self.done)


@total_ordering
class SocialNetworkPost:
    def __init__(self, user: str, content: str):
        self._user = user
        self._content = content

    @property
    def user(self) -> str:
        return self._user

    @property
    def content(self) -> str:
        return self._content

    def done(self) -> bool:
        ...
        
    def save(self) -> str:
        ...

    def likes(self) -> List['SocialNetworkUser']:
        ...

    def remove(self, user: str):
        ...

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return self.likes() < other.likes()


@total_ordering
class SocialNetworkUser:
    def __init__(self, vertex: DSADirectedGraphVertex, posts: DSALinkedList):
        self._vertex = vertex
        self._posts = posts

    def posts(self) -> List['SocialNetworkPost']:
        ...

    def followers(self) -> List['SocialNetworkUser']:
        # Requires caching of followers in DSADirectedGraph
        ...

    def following(self) -> List['SocialNetworkUser']:
        ...

    def name(self) -> str:
        return self._vertex.label

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return len(self.followers()) < len(other.followers())
