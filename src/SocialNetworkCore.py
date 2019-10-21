from typing import List
from functools import total_ordering
import unittest
from itertools import chain

from numpy.random import binomial

from ADT.DSADirectedGraph import DSADirectedGraph, DSADirectedGraphVertex
from ADT.DSALinkedList import DSALinkedList, DSAListNode
from ADT.DSAHeap import DSAHeap

class SocialNetwork:
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
        self._posts = DSALinkedList()
        self._postLikes = DSAHeap()

    @property
    def probLike(self) -> float:
        return self._probLike

    @probLike.setter
    def probLike(self, prob: float):
        SocialNetwork._checkProb(prob)
        self._probLike = prob

    @property
    def probFollow(self) -> float:
        return self._probFollow

    @probFollow.setter
    def probFollow(self, prob: float):
        SocialNetwork._checkProb(prob)
        self._probFollow = prob

    def loadNetwork(self, file):
        # Remove existing network and posts
        self._network = DSADirectedGraph()
        self._posts = DSALinkedList()
        self._postLikes = DSAHeap()
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

    def follow(self, follower: str, followed: str):
        # Return false if the user is already following
        ret = True
        if follower == followed:
            raise ValueError("User cannot follow themselves.")
        if self._network.hasEdge(follower, followed):
            ret = False
        else:
            try:
                self._network.addEdge(follower, followed)
            except ValueError as e:
                raise ValueError(SocialNetwork.USER_NOT_EXIST) from e
        return ret

    def unfollow(self, follower: str, followed: str):
        try:
            self._network.removeEdge(follower, followed)
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e

    def like(self, user: str):
        if len(self._posts) != 0:
            try:
                u = self.findUser(user)
                self._posts.peekFirst().like(u)
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
            if self._posts.peekFirst().unlike(u) is None:
                raise ValueError("User has not liked this post.")
        else:
            raise ValueError("There are no posts to unlike.")

    def addUser(self, user: str):
        if self._network.hasVertex(user):
            raise ValueError("User already exists.")
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
            self._posts.peekFirst().update()
        else:
            raise ValueError("Network cannot be updated.")

    def save(self) -> str:
        return self._network.displayExploded()

    def addPost(self, userName: str, content: str, clickbaitFactor: float = 1):
        try:
            user = self.findUser(userName)
            self._posts.insertFirst(SocialNetworkPost(user, content, self, clickbaitFactor))
            self._postLikes.add(self._posts.peekFirst(), None)
            user.addPost(self._posts.peekFirst())
        except ValueError as e:
            raise ValueError((f"Could not create post. User: {userName}, ",
                              f"Clickbait factor: {clickbaitFactor}")) from e

    def done(self) -> bool:
        return len(self._posts) == 0 or self._posts.peekFirst().done()

    # Statistics methods

    def simstate(self) -> str:
        """Outputs all statistics required for the simulation timestep.

        Returns:
            Network representation, most recent post representation,
            and optional statistics.
        """
        return f"{self.save()}\n{self._posts.peekFirst().save()}\n"#{self.optionalStats()}\n"

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
            totalLikes = sum([sum(1 for _ in x.liked()) for x in self._posts])
            averageLikes = totalLikes / (len(self._posts) * self._network.getVertexCount())
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
        sumLocalClustering = 0
        for k, v in self._network:
            # Find clusting coefficient of node
            # First, find the neighbourhood
            import copy
            neighbourhood = copy.copy(v.successor)
            for preK, preV in v.predecessor:
                if not neighbourhood.hasKey(preK):
                    neighbourhood.put(preK, preV)
            # Next, find the number of connections between nodes in the neighbourhood
            connectionCount = 0
            for nK, nV in neighbourhood:
                for succK, succV in nV.successor:
                    if neighbourhood.hasKey(succK):
                        connectionCount += 1
            if len(neighbourhood) != 0 and len(neighbourhood) != 1:
                sumLocalClustering += connectionCount / ((len(neighbourhood) - 1) * len(neighbourhood))
        globalCoef = 0
        if self._network.getVertexCount() != 0:
            globalCoef = sumLocalClustering / self._network.getVertexCount()
        return globalCoef

    def popularPosts(self) -> List['SocialNetworkPost']:
        self._postLikes._heapify()
        return [x[0] for x in self._postLikes.sort()]

    def popularUsers(self) -> List['SocialNetworkUser']:
        self._mostFollowed._heapify()
        return [x[0] for x in self._mostFollowed.sort()]

    # Private methods

    @staticmethod
    def _checkProb(prob):
        if prob < 0 or prob > 1:
            raise ValueError("Probabilities must be in the range [0, 1]")

    def _canUpdate(self) -> bool:
        return (self._probFollow != -1.0
                and self._probLike != -1.0
                and self._network.getVertexCount() != 0
                and not self.done())


@total_ordering
class SocialNetworkPost:
    def __init__(self, user: 'SocialNetworkUser', content: str, network: 'SocialNetwork',
                 clickbaitFactor):
        self._recentlyLiked = DSALinkedList()
        self._liked = DSALinkedList()
        self._recentlyLiked.insertFirst(user)
        self._content = content
        self._network = network
        self.clickbaitFactor = clickbaitFactor

    @property
    def clickbaitFactor(self):
        return self._clickbaitFactor

    @clickbaitFactor.setter
    def clickbaitFactor(self, clickbaitFactor: float):
        if clickbaitFactor < 0:
            raise ValueError("clickbaitFactor must be positive.")
        self._clickbaitFactor = clickbaitFactor

    def user(self) -> 'SocialNetworkUser':
        if len(self._liked) == 0:
            user = self._recentlyLiked.peekLast()
        else:
            user = self._liked.peekLast()
        return user

    def like(self, user: 'SocialNetworkUser'):
        if self._recentlyLiked.find(user) or self._liked.find(user):
            raise ValueError("User has already liked post.")
        self._recentlyLiked.insertFirst(user)

    def unlike(self, user: 'SocialNetworkUser'):
        ret = self._liked.remove(user)
        if ret is None:
            ret = self._recentlyLiked.remove(user)
        return ret

    @property
    def content(self) -> str:
        return self._content

    def done(self) -> bool:
        return len(self._recentlyLiked) == 0
        
    def save(self) -> str:
        return (f"content: {self.content}\nuser: {self.user().name()}\nliked:\n"
                + '\n'.join([x.name() for x in self.liked()]) + '\n')

    def update(self) -> str:
        # The core of the algorithm. (Finally!)
        newLikes = DSALinkedList()
        for x in self._recentlyLiked:
            for user in x.followers():
                # Does the user like the post?
                if binomial(1, min(1, self._network.probLike * self.clickbaitFactor)) == 1:
                    if not self._liked.find(user) and not self._recentlyLiked.find(user):
                        newLikes.insertFirst(user)
                    # Does the user follow the original poster?
                    if binomial(1, self._network.probFollow) == 1:
                        try:
                            self._network.follow(user.name(), self.user().name())
                        except ValueError:
                            pass
        self._liked = self._recentlyLiked.concat(self._liked)
        self._recentlyLiked = newLikes

    def liked(self):
        def generateLiked(l1, l2):
            for x in l1:
                yield x
            for x in l2:
                yield x
        return generateLiked(self._recentlyLiked, self._liked)

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        return (len(self._liked) + len(self._recentlyLiked)
                < len(other._recentlyLiked) + len(other._liked))


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


class SocialNetworkTest(unittest.TestCase):
    def testAddUser(self):
        network = SocialNetwork()
        network.addUser("Jakob Wyatt")
        network.addUser("Art Page")

    def testFindUser(self):
        network = SocialNetwork()
        network.addUser("Jakob Wyatt")
        network.addUser("beach")
        user = network.findUser("Jakob Wyatt")
        beach = network.findUser("beach")
        self.assertRaises(ValueError, network.findUser, "byte")
        self.assertEqual(user.name(), "Jakob Wyatt")
        self.assertEqual(beach.name(), "beach")

    def testFollow(self):
        network = SocialNetwork()
        network.addUser("Jakob Wyatt")
        network.addUser("Imagination")
        user = network.findUser("Jakob Wyatt")
        imag = network.findUser("Imagination")
        self.assertEqual(len(user.followers()), 0)
        self.assertEqual(len(user.following()), 0)
        network.follow("Jakob Wyatt", "Imagination")
        self.assertEqual(len(user.followers()), 0)
        self.assertEqual(len(user.following()), 1)
        self.assertEqual(len(imag.followers()), 1)
        self.assertEqual(len(imag.following()), 0)
        self.assertRaises(ValueError, network.follow, "Jakob Wyatt", "Non existent")
        network.follow("Imagination", "Jakob Wyatt")
        self.assertEqual(len(user.followers()), 1)
        self.assertEqual(len(user.following()), 1)
        self.assertEqual(len(imag.followers()), 1)
        self.assertEqual(len(imag.following()), 1)
        network.addUser("example")
        network.follow("example", "Imagination")
        network.follow("Jakob Wyatt", "example")
        self.assertEqual(len(user.followers()), 1)
        self.assertEqual(len(user.following()), 2)
        self.assertEqual(len(imag.followers()), 2)
        self.assertEqual(len(imag.following()), 1)

    def testUnfollow(self):
        network = SocialNetwork()
        network.addUser("a")
        network.addUser("b")
        network.addUser("c")
        network.follow("a", "b")
        network.follow("b", "c")
        a = network.findUser("a")
        b = network.findUser("b")
        c = network.findUser("c")
        network.follow("c", "a")
        network.follow("b", "a")
        self.assertEqual(len(a.followers()), 2)
        self.assertEqual(len(a.following()), 1)
        self.assertEqual(len(b.followers()), 1)
        self.assertEqual(len(b.following()), 2)
        self.assertEqual(len(c.followers()), 1)
        self.assertEqual(len(c.following()), 1)
        network.unfollow("c", "a")
        network.unfollow("a", "b")
        self.assertEqual(len(a.followers()), 1)
        self.assertEqual(len(a.following()), 0)
        self.assertEqual(len(b.followers()), 0)
        self.assertEqual(len(b.following()), 2)
        self.assertEqual(len(c.followers()), 1)
        self.assertEqual(len(c.following()), 0)

    def testNewPost(self):
        network = SocialNetwork()
        network.addUser("Jakob")
        network.addPost("Jakob", "In bali atm")
        jakob = network.findUser("Jakob")
        self.assertEqual(len(jakob.posts), 1)
        network.addPost("Jakob", "Generic Meme")
        self.assertEqual(len(jakob.posts), 2)

    def testLikeUnlike(self):
        network = SocialNetwork()
        network.addUser("Jakob")
        network.addUser("Tom")
        network.addUser("Ben")
        network.addPost("Jakob", "In bali atm")
        network.like("Ben")
        network.addPost("Jakob", "bad content")
        network.like("Tom")
        network.like("Ben")
        network.addPost("Jakob", "meme")
        for x1, x2 in zip(network.popularPosts(), ["bad content", "In bali atm", "meme"]):
            self.assertEqual(x2, x1.content)

    def d_testLoadSaveNetwork(self):
        network = SocialNetwork()
        network2 = SocialNetwork()
        with open("../example/dark_crystal_net.txt", "r") as f:
            network.loadNetwork(f)
            network2.loadNetwork(network.save().split('\n'))
            for x1, x2 in zip(network2.save().split('\n'), network.save().split('\n')):
                self.assertEqual(x1.rstrip('\n'), x2.rstrip('\n'))

    def testSavePost(self):
        network = SocialNetwork()
        network.addUser("Jakob")
        network.addUser("bruh")
        network.addUser("moment")
        network.addPost("Jakob", "Wow content")
        network.like("bruh")
        network.like("moment")
        self.assertEqual(network._posts.peekFirst().save(),
                         ("content: Wow content\n"
                          "user: Jakob\n"
                          "liked:\n"
                          "moment\n"
                          "bruh\n"
                          "Jakob\n"))

    def testPopularUser(self):
        network = SocialNetwork()
        network.addUser("a")
        network.addUser("b")
        network.addUser("c")
        network.addUser("d")
        network.addUser("e")
        network.follow("b", "a")
        network.follow("c", "a")
        network.follow("d", "a")
        network.follow("e", "a")
        network.follow("c", "b")
        network.follow("d", "b")
        network.follow("e", "b")
        network.follow("d", "c")
        network.follow("e", "c")
        network.follow("e", "d")
        for x1, x2 in zip(network.popularUsers(), ["a", "b", "c", "d", "e"]):
            self.assertEqual(x1.name(), x2)
        network.removeUser("a")
        network.removeUser("e")
        network.removeUser("c")
        network.unfollow("d", "b")
        network.follow("b", "d")
        for x1, x2 in zip(network.popularUsers(), ['d', 'b']):
            self.assertEqual(x1.name(), x2)


if __name__ == "__main__":
    unittest.main()
