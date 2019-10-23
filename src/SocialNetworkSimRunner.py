from ADT.DSADirectedGraph import *
from ADT.DSALinkedList import *
from SocialNetworkCore import SocialNetwork

import random
import math
import numpy
import itertools

class SocialNetworkSimRunner:
    """
    This class contains miscellaneous functions used to run individual simulations,
    orchestrate multiple simulations, and generate simulation data.
    These were all put into one class as they had similar functionality,
    despite not sharing any data or state between them.
    """

    @staticmethod
    def SimulationInterface(netfile, eventfile, prob_like, prob_foll):
        try:
            fileName, _ = Simulation(netfile, eventfile, prob_like, prob_foll)
            print(f"Simulation logged to {fileName}")
        except ValueError as ex:
            print(str(ex))
            raise ex

    @staticmethod
    def Simulation(netfile, eventfile, prob_like, prob_foll) -> (str, DSALinkedList):
        network = SocialNetwork(probLike=prob_like, probFollow=prob_foll)
        network.loadNetwork(netfile)
        events = [x.rstrip('\n') for x in eventfile]
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False, mode='w') as f:
            filename = f.name
            fileData, stats = ExecEventFile(network, events)
            f.write(fileData)
        return filename, stats

    @staticmethod
    def ExecEventFile(network, eventFile) -> (str, DSALinkedList):
        outcome = ""
        from collections import namedtuple
        SimStats = namedtuple('SimStats', 'post likes clustering favg fsd')
        stats = DSALinkedList()
        post = 0
        for x in eventFile:
            tokens = x.split(':')
            if len(tokens) == 3 and tokens[0] == "F":
                network.follow(tokens[2], tokens[1])
            elif len(tokens) == 3 and tokens[0] == "U":
                network.unfollow(tokens[2], tokens[1])
            elif len(tokens) == 2 and tokens[0] == "A":
                network.addUser(tokens[1])
            elif len(tokens) == 2 and tokens[0] == "R":
                network.removeUser(tokens[1])
            elif len(tokens) == 3 or len(tokens) == 4 and tokens[0] == "P":
                if len(tokens) == 3:
                    network.addPost(tokens[1], tokens[2])
                else:
                    network.addPost(tokens[1], tokens[2], float(tokens[3]))
                while not network.done():
                    stats.insertLast(SimStats(post, network.likesScaled(),
                                               network.clusteringCoefficient(), *network.followsAvSd()))
                    outcome += network.simstate()
                    outcome += (f"Likes per person per post: {stats.peekFirst().likes}\n"
                                f"Follower Average: {stats.peekFirst().favg}\nFollower s.d: {stats.peekFirst().fsd}\n"
                                f"Clustering Coefficient: {stats.peekFirst().clustering}")
                    network.update()
                post += 1
            else:
                raise ValueError("Invalid file format.")
        return outcome, stats

    @staticmethod
    def GenerateSocialNetworkAndPost(*, size: int, follower_av: float, follower_sd: float,
                              clustering_func, post_num, clickbait_sd) -> (str, str):
        """
        This method generates a social network with given parameters, and writes it
        to a file.
        The algorithm used to generate this network was created by the author,
        and to their knowledge, does not exist anywhere else.
        First, a number of verticies are created equal to the input parameter size.
        Next, these verticies are iterated over, and the number of successors of each
        vertex is calculated by sampling from a distribution X ~ N(follower_av, follwer_sd^2).

        To select the edges of the network, an approach similar in nature to a variogram
        (https://en.wikipedia.org/wiki/Variogram) was used (taken from the field of geostatistics).
        A variogram measures the amount of correlation between two points that are some distance apart.
        In this algorithm, this distance is discrete rather than continuous, and is measured by finding
        a path between two nodes.
        This gives some way of changing the clustering coefficient of a graph, as a graph with high
        clustering coefficient will have a higher number of connections to 'nearby' verticies.

        To sample an edge from this variogram, a random walk is performed starting at a given vertex.
        This random walk occurs along any nodes that are predecessors of the current node,
        and does not loop back onto previously visited nodes.
        At each step on the random walk, the probability of adding an edge with the current vertex
        is calculated by evaluating the clustering_func at the distance from the original node.
        If a follow occurs, the process
        starts again and repeats until all necessary edges have been created.
        If there are no valid nodes to walk to,
        or has reached some distance threshold from the original node,
        a random node from the graph is chosen to follow. This allows initial
        'bootstrapping' of the network when no edges have yet been created.
        """
        network = DSADirectedGraph()
        # Add verticies
        for x in range(size):
            # Value is number of followers
            network.addVertex(f"A{x}", min(size - 1, max(0, int(random.gauss(follower_av, follower_sd)))))
        # Add edges
        for n in range(size):
            node = network.getVertex(f"A{n}")
            for x in range(node.value):
                # Randomly walk through graph via "followed" connections, with a decreasing chance of following.
                # If an end is reached, or a certain threshold, then a random node is selected to be connected.
                threshold = 5
                walk = DSALinkedList()
                walk.insertLast(node)
                exhausted = False
                done = False
                while len(walk) - 1 < threshold and not exhausted and not done:
                    valid_nodes = list(filter(lambda x: not walk.find(x), [v for _, v in walk.peekFirst().predecessor]))
                    if len(valid_nodes) == 0:
                        exhausted = True
                    else:
                        walk.insertFirst(random.choice(valid_nodes))
                        if numpy.random.binomial(1, clustering_func(len(walk))) and (not node.successor.hasKey(walk.peekFirst().label)):
                            done = True
                            network.addEdge(node.label, walk.peekFirst().label)
                # Follow someone random if no-one was followed during the random walk.
                if not done:
                    # Inefficient
                    possibleNodes = [f"A{x}" for x in range(size)]
                    successorLabels = [k for k, _ in node.successor]
                    possibleNodes = list(filter(lambda x: (x not in successorLabels) and x != node.label, possibleNodes))
                    network.addEdge(node.label, random.choice(possibleNodes))
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(delete=False, mode='w') as f:
            netFilename = f.name
            f.write(network.displayExploded())
        # Generate Posts
        with NamedTemporaryFile(delete=False, mode='w') as f:
            postFilename = f.name
            for _ in range(post_num):
                postNode = f"A{random.choice(range(size))}"
                f.write(f"P:{postNode}:CONTENT:{max(0, random.gauss(1, clickbait_sd))}\n")
        return netFilename, postFilename

    @staticmethod
    def GridSearch(stream):
        """
        This method uses the gridsearch algorithm to search through a large parameter space,
        and measure the output of a function at many points in the space.
        These outputs are then logged to a file as csv data, and can be used for further analysis.

        Parameters that are varied in this function are the like and follow probabilities,
        network size, clickbait standard deviation, post/timestep number, and
        follower average (density) / follower standard deviation (relative popularity).

        In this algorithm, for each possible combination of the parameter arrays
        (n-dimensional grid), a network using these parameters is generated,
        and a simulation of that network is run..

        An advantage of this algorithm is that it is very easy to implement compared to
        other search space algorithms, such as gradient descent and evolution.
        However, a disadvantage is that it searches a very large volume when the parameter
        space has many dimensions (curse of dimensionality), causing a large amount of data 
        to be produced at a very high runtime.
        """
        like_prob = [0.2, 0.4, 0.6, 0.8, 1]
        foll_prob = [0.2, 0.4, 0.6, 0.8, 1]
        size = [25]
        follower_average_mult_sz = [0.5]
        follower_sd_mult_av = [0.5]
        clickbait_sd = [0]
        posts = 10
        outputCsv = ""
        for lp in like_prob:
            for fp in foll_prob:
                for sz in size:
                    for favg in follower_average_mult_sz:
                        for fsd in follower_sd_mult_av:
                            for csd in clickbait_sd:
                                files = GenerateSocialNetworkAndPost(size=sz, follower_av=favg * sz, follower_sd=fsd * favg * sz,
                                                                     clustering_func=lambda x: 0, post_num=posts, clickbait_sd=csd)
                                with open(files[0], 'r') as net, open(files[1], 'r') as event:
                                    _, stats = simulation(net, event, lp, fp)
                                stream(f"\n\nlike_prob:{lp},follow_prob:{fp},size:{sz},follower_average_mult_sz:{favg},follower_sd_mult_av:{fsd},clickbait_sd:{csd}\n")
                                stream("post,likes,clustering,favg,fsd\n")
                                stream("\n".join([f"{x.post},{x.likes},{x.clustering},{x.favg},{x.fsd}" for x in stats]))


if __name__ == "__main__":
    with open("../report/subset.csv", "w") as f:
        def printAndWrite(x):
            print(x, end='')
            f.write(x)
        SocialNetworkSimRunner.GridSearch(printAndWrite)
