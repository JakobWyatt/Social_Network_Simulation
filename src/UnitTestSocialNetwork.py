import unittest

from SocialNetworkCore import SocialNetwork
from SocialNetworkSimRunner import SocialNetworkSimRunner

class UnitTestSocialNetwork(unittest.TestCase):
    """
    This class contains unittests for the SocialNetwork class.
    """

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
        self.assertTrue(network.unfollow("c", "a"))
        self.assertTrue(network.unfollow("a", "b"))
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
        self.assertEqual(network._currentPost.save(),
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

    def testPropogatePost(self):
        # Algorithm is deterministic when probabilities = 1
        with open("../example/doremi.net", 'r') as net, open("../example/doremi.e2", 'r') as event, open("../example/doremi.e2.output", 'r') as expected:
            outputFile = SocialNetworkSimRunner.SimulationInterface(net, event, 1, 1)
            with open(outputFile, 'r') as out:
                for x1, x2 in zip(out, expected):
                    self.assertEqual(x1, x2)


if __name__ == "__main__":
    unittest.main()
