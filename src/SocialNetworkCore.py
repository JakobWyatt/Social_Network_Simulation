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
        self._posts = DSALinkedList()
        self._postLikes = DSAHeap()

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
        if self._network.hasVertex(user):
            raise ValueError("User already exists.")
        self._network.addVertex(user, None)

    def removeUser(self, user: str):
        ...

    def findUser(self, user: str) -> 'SocialNetworkUser':
        return SocialNetworkUser(self._network.getVertex(user))

    def display(self):
        self._network.render()

    def update(self):
        ...

    def save(self) -> str:
        ...

    def addPost(self, userName: str, content: str):
        user = self.findUser(userName)
        self._posts.insertFirst(SocialNetworkPost(user, content))
        self._postLikes.add(self._posts.peekFirst(), None)
        user.addPost(self._posts.peekFirst())

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
        self._postLikes._heapify()
        return [x[0] for x in self._postLikes.sort()]

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
    def __init__(self, user: 'SocialNetworkUser', content: str):
        self._liked = DSALinkedList()
        self._liked.insertFirst(user)
        # Inclusive range from start to endRecentlyLiked
        self._endRecentlyLiked = user
        self._content = content

    def user(self) -> 'SocialNetworkUser':
        return self._liked.peekLast()

    @property
    def content(self) -> str:
        return self._content

    def done(self) -> bool:
        ...
        
    def save(self) -> str:
        ...

    @property
    def liked(self) -> DSALinkedList:
        return self._liked

    def remove(self, user: str):
        ...

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return len(self.liked) < len(other.liked)


@total_ordering
class SocialNetworkUser:
    def __init__(self, vertex: DSADirectedGraphVertex):
        self._vertex = vertex
        self._posts = DSALinkedList()

    def posts(self) -> List['SocialNetworkPost']:
        ...

    def addPost(self, post: 'SocialNetworkPost'):
        self._posts.insertFirst(post)

    def followers(self) -> List['SocialNetworkUser']:
        ...

    def following(self) -> List['SocialNetworkUser']:
        ...

    def name(self) -> str:
        return self._vertex.label

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return len(self.followers()) < len(other.followers())
