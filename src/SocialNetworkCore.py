from typing import List

from ADT.DSADirectedGraph import *
from ADT.DSAHeap import *
from ADT.DSAHashTable import *
from ADT.DSALinkedList import *

from SocialNetworkUser import SocialNetworkUser
from SocialNetworkPost import SocialNetworkPost


class SocialNetwork:
    """
    This class contains an interface for creating and updating a social
    network, and contains common functionality used in both interactive and
    simulation mode. By doing this, the underlying data structures used to
    store the network an be changed without needing to also change the user
    interface code.
    """

    # Error messages
    USER_NOT_EXIST = "User does not exist."

    def __init__(self, *, probLike=-1.0, probFollow=-1.0):
        if probLike == -1.0 and probFollow == -1.0:
            self._probLike = -1.0
            self._probFollow = -1.0
        else:
            self.probLike = probLike
            self.probFollow = probFollow
        self._network = DSADirectedGraph()
        self._mostFollowed = DSAHeap()
        self._currentPost = None
        # Post likes
        self._posts = DSAHeap()

    @property
    def probLike(self) -> float:
        return self._probLike

    @probLike.setter
    def probLike(self, prob: float):
        if prob < 0 or prob > 1:
            raise ValueError("Probabilities must be in the range [0, 1]")
        self._probLike = prob

    @property
    def probFollow(self) -> float:
        return self._probFollow

    @probFollow.setter
    def probFollow(self, prob: float):
        if prob < 0 or prob > 1:
            raise ValueError("Probabilities must be in the range [0, 1]")
        self._probFollow = prob

    def loadNetwork(self, file):
        # Remove existing network and posts
        self._network = DSADirectedGraph()
        self._posts = DSAHeap()
        self._currentPost = None
        for x in file:
            formatted = x.rstrip('\n').split(':')
            if len(formatted) == 1:
                # Add user
                if len(formatted[0]) != 0:
                    self.addUser(formatted[0])
            elif len(formatted) == 2:
                # Add follow
                self.follow(formatted[1], formatted[0])
            else:
                raise ValueError("Invalid file.")

    def follow(self, follower: str, followed: str) -> bool:
        ret = False
        user1 = None
        user2 = None
        try:
            user1 = SocialNetworkUser(self._network.getVertex(follower))
            user2 = SocialNetworkUser(self._network.getVertex(followed))
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
        if user1 is not None and user2 is not None:
            ret = user1.follow(user2)
        return ret

    def unfollow(self, follower: str, followed: str) -> bool:
        ret = False
        user1 = None
        user2 = None
        try:
            user1 = SocialNetworkUser(self._network.getVertex(follower))
            user2 = SocialNetworkUser(self._network.getVertex(followed))
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
        if user1 is not None and user2 is not None:
            ret = user1.unfollow(user2)
        return ret

    def like(self, user: str):
        if len(self._posts) != 0:
            try:
                u = self.findUser(user)
                self._currentPost.like(u)
            except ValueError as e:
                raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
        else:
            raise ValueError("There are no posts to like.")

    def unlike(self, user: str):
        if len(self._posts) != 0:
            try:
                u = self.findUser(user)
            except ValueError as e:
                raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
            if self._currentPost.unlike(u) is None:
                raise ValueError("User has not liked this post.")
        else:
            raise ValueError("There are no posts to unlike.")

    def addUser(self, user: str):
        if ":" in user:
            raise ValueError(f"Invalid username.")
        if self._network.hasVertex(user):
            raise ValueError(f"{user} already exists.")
        # Value is cached posts
        self._network.addVertex(user, DSALinkedList())
        self._mostFollowed.add(self.findUser(user), None)

    def removeUser(self, user: str):
        try:
            self._mostFollowed.removeArbitrary(self.findUser(user))
            self._network.removeVertex(user)
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e

    def findUser(self, userName: str) -> 'SocialNetworkUser':
        user = None
        try:
            user = SocialNetworkUser(self._network.getVertex(userName))
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
        return user

    def display(self):
        self._network.render()

    def update(self):
        if self._canUpdate():
            self._currentPost.update()
        else:
            raise ValueError("Network cannot be updated.")

    def save(self) -> str:
        return self._network.displayExploded()

    def addPost(self, userName: str, content: str, clickbaitFactor: float = 1):
        try:
            user = self.findUser(userName)
            self._currentPost = SocialNetworkPost(user, content,
                                                  clickbaitFactor,
                                                  self.probLike,
                                                  self.probFollow)
            self._posts.add(self._currentPost, None)
            user.addPost(self._currentPost)
        except ValueError as e:
            raise ValueError("Could not create post.") from e

    def done(self) -> bool:
        return len(self._posts) == 0 or self._currentPost.done()

    # Statistics methods

    def simstate(self) -> str:
        """Outputs all statistics required for the simulation timestep.

        Returns:
            Network representation, most recent post representation,
            and optional statistics.
        """
        return f"{self.save()}\n{self._currentPost.save()}\n"

    def optionalStats(self) -> str:
        """Outputs optional statistics about the network.
        """
        followAv, followSd = self.followsAvSd()
        return (f"Likes per person per post: {self.likesScaled()}\n"
                f"Follower Average: {followAv}\nFollower s.d: {followSd}\n"
                f"Clustering Coefficient: {self.clusteringCoefficient()}")

    def likesScaled(self) -> float:
        # Likes per person per post
        averageLikes = 0
        if len(self._posts) * self._network.getVertexCount() != 0:
            totalLikes = sum([sum(1 for _ in x.priority.liked())
                             for x in self._posts])
            averageLikes = totalLikes / (len(self._posts) *
                                         self._network.getVertexCount())
        return averageLikes

    def followsAvSd(self) -> (float, float):
        import statistics
        followNums = [len(v.successor) for _, v in self._network]
        avFoll = 0
        sdFoll = 0
        if len(followNums) != 0:
            avFoll = sum(followNums) / len(followNums)
            sdFoll = statistics.pstdev(followNums)
        return avFoll, sdFoll

    def clusteringCoefficient(self) -> float:
        """
        Calculates the globally averaged/scaled local clustering coefficient
        of a graph. This algorithm can be found here:
        https://en.wikipedia.org/wiki/Clustering_coefficient

        The top level description of this algorithm is that for each node,
        a 'local clustering coeffient' is calculated. The number returned
        from this function is the average of all local clustering coefficients
        of the network, divided by the number of follows in the network.
        This is done to avoid the influence increasing followers has on the
        clustering coefficient.

        To calculate the clustering coeffient of a user, the neighbourhood of
        the user is first found. This is defined as the union of the people
        that are followed by, and following, the user.
        Next, for every connection of every user in the neighbourhood,
        the number of connections that lie within that
        neighbourhood are counted.
        Finally, the number of connections within the neighbourhood are
        divided by the total number of potential connections within the
        neighbourhood, (neighbourhood_size * (neighbourhood_size - 1)).

        This algorithm has O(n^3) execution time when hashtables are used to
        store edges and verticies. When a linked list is used instead, this
        execution time jumps to O(n^4).
        """
        sumLocalClustering = 0
        for k, v in self._network:
            # Find clusting coefficient of node
            # First, find the neighbourhood
            neighbourhood = DSAHashTable()
            for k, v in v.successor:
                neighbourhood.put(k, v)
            for preK, preV in v.predecessor:
                if not neighbourhood.hasKey(preK):
                    neighbourhood.put(preK, preV)
            # Next, find the number of connections between
            # nodes in the neighbourhood
            connectionCount = 0
            for nK, nV in neighbourhood:
                for succK, succV in nV.successor:
                    if neighbourhood.hasKey(succK):
                        connectionCount += 1
            if len(neighbourhood) != 0 and len(neighbourhood) != 1:
                sumLocalClustering += (connectionCount /
                                       ((len(neighbourhood) - 1)
                                        * len(neighbourhood)))
        globalCoef = 0
        if (self._network.getVertexCount() != 0
           and self._network.getEdgeCount() != 0):
            globalCoef = sumLocalClustering / (self._network.getVertexCount()
                                               * self._network.getEdgeCount())
        return globalCoef

    def popularPosts(self) -> List['SocialNetworkPost']:
        self._posts._heapify()
        return [x[0] for x in self._posts.sort()]

    def popularUsers(self) -> List['SocialNetworkUser']:
        self._mostFollowed._heapify()
        return [x[0] for x in self._mostFollowed.sort()]

    # Private methods
    def _canUpdate(self) -> bool:
        return (self._probFollow != -1.0
                and self._probLike != -1.0
                and self._network.getVertexCount() != 0
                and not self.done())
