from typing import List

from ADT.DSADirectedGraph import DSADirectedGraph, DSADirectedGraphVertex
from ADT.linkedLists import DSALinkedList, DSAListNode


class SocialNetwork:
    def __init__(self):
        self._probLike = -1.0
        self._probFollow = -1.0
        self._network = DSADirectedGraph()
        self._posts = DSALinkedList()

    def __init__(self, *, probLike=-1.0, probFollow=-1.0):
        if probLike == -1.0 and probFollow == -1.0:
            self._probLike = -1.0
            self._probFollow = -1.0
        else:
            self.probLike = probLike
            self.probFollow = probFollow
        self._network = DSADirectedGraph()
        self._posts = DSALinkedList()

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
        ...

    def unfollow(self, follower: str, followed: str):
        ...

    def like(self, user: str, postId: int):
        ...

    def unlike(self, user: str, postId: int):
        ...

    def addUser(self, user: str):
        ...

    def removeUser(self, user: str):
        ...

    def findUser(self, user: str) -> 'SocialNetworkUser':
        ...

    def display(self):
        ...

    def update(self):
        ...

    def save(self) -> str:
        ...

    def addPost(self, user: str, content: str) -> int:
        ...

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


class SocialNetworkPost:
    def __init__(self, network: DSADirectedGraph, user: str, content: str, id: int):
        self._network = network
        self._user = user
        self._content = content
        self._id = id

    @property
    def user(self) -> str:
        return self._user

    @property
    def content(self) -> str:
        return self._content

    def id(self) -> int:
        return self._id

    def done(self) -> bool:
        ...
        
    def save(self) -> str:
        ...

    def likes(self) -> List['SocialNetworkUser']:
        ...


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