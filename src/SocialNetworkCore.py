from typing import List
from functools import total_ordering
import unittest

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
        self.probLike = prob

    @property
    def probFollow(self) -> float:
        return self._probFollow

    @probFollow.setter
    def probFollow(self, prob: float):
        SocialNetwork._checkProb(prob)
        self.probFollow = prob

    def loadNetwork(self, file):
        # Remove existing network and posts
        self._network = DSADirectedGraph()
        self._posts = DSALinkedList()
        self._postLikes = DSAHeap()
        for x in file:
            formatted = x.rstrip('\n').split(':')
            if len(formatted) == 1:
                # Add user
                self.addUser(formatted[0])
            elif len(formatted) == 2:
                # Add follow
                self.follow(formatted[0], formatted[1])
            else:
                raise ValueError("Invalid file.")

    def follow(self, follower: str, followed: str):
        if follower == followed:
            raise ValueError("User cannot follow themselves.")
        try:
            self._network.addEdge(follower, followed)
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e

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

    def addPost(self, userName: str, content: str):
        try:
            user = self.findUser(userName)
            self._posts.insertFirst(SocialNetworkPost(user, content))
            self._postLikes.add(self._posts.peekFirst(), None)
            user.addPost(self._posts.peekFirst())
        except ValueError as e:
            raise ValueError(SocialNetwork.USER_NOT_EXIST) from e

    def done(self) -> bool:
        return len(self._posts) == 0 or self._posts.peekFirst().done()

    # Statistics methods

    def simstate(self) -> str:
        """Outputs all statistics required for the simulation timestep.

        Returns:
            Network representation, most recent post representation,
            and optional statistics.
        """
        return f"{self.save()}\n{self._posts.peekFirst().save()}\n{self.optionalStats()}\n"

    def optionalStats(self) -> str:
        """Outputs optional statistics about the network.
        """
        return ""

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
    def __init__(self, user: 'SocialNetworkUser', content: str):
        self._recentlyLiked = DSALinkedList()
        self._liked = DSALinkedList()
        self._recentlyLiked.insertFirst(user)
        self._content = content

    def user(self) -> 'SocialNetworkUser':
        if len(self._liked) == 0:
            user = self._recentlyLiked.peekLast()
        else:
            user = self._liked.peekLast()
        return user

    def like(self, user: 'SocialNetworkUser'):
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
        return (f"content: {self.content}\nuser: {self.user().name()}\n"
                + '\n'.join([x.name() for x in self.liked()]) + '\n')

    def update(self) -> str:
        # The core of the algorithm. (Finally!)
        # Keep track of the original head of the list,
        # which will be the first element that has already been evaluated.
        # New likers are added to the list.
        # Some list internals will be used here to more effectively split
        # the list into parts.
        head = self._liked._head
        # Temporarily make an exclusive range at the end for ease of comparison
        
    def liked(self) -> DSALinkedList:
        from copy import copy
        return copy(self._recentlyLiked).concat(copy(self._liked))

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
        return [SocialNetworkUser(x) for x in self._vertex.predecessor]

    def following(self) -> List['SocialNetworkUser']:
        return [SocialNetworkUser(x) for x in self._vertex.successor]

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

    def testLoadSaveNetwork(self):
        network = SocialNetwork()
        with open("../example/network_file.txt", "r") as f:
            network.loadNetwork(f)
            f.seek(0)
            for x1, x2 in zip(f, network.save().split('\n')):
                self.assertEqual(x1.rstrip('\n'), x2)

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
