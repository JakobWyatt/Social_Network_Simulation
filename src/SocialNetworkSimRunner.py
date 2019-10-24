import random
import math
import itertools
from typing import Callable
from tempfile import NamedTemporaryFile

import numpy

from ADT.DSADirectedGraph import *
from ADT.DSALinkedList import *
from SocialNetworkCore import SocialNetwork


class SocialNetworkSimRunner:
    """
    This class contains miscellaneous functions used to run individual
    simulations, orchestrate multiple simulations, and generate simulation
    data. These were all put into one class as they had similar functionality,
    despite not sharing any data or state between them.
    """

    @staticmethod
    def SimulationInterface(netfile, eventfile, prob_like, prob_foll):
        filename = None
        try:
            state = SocialNetworkSimRunner.Simulation(netfile, eventfile,
                                                      prob_like, prob_foll)
            with NamedTemporaryFile(delete=False, mode='w') as f:
                filename = f.name
                for x in state:
                    f.write(f"{x.simstate}"
                            f"Likes per person per post: {x.likes}\n"
                            f"Follower Average: {x.favg}\n"
                            f"Follower s.d: {x.fsd}\n"
                            f"Clustering Coefficient: {x.clustering}\n\n")
        except ValueError as ex:
            print(str(ex))
        return filename

    @staticmethod
    def Simulation(netfile, eventfile, prob_like, prob_foll) -> DSALinkedList:
        network = SocialNetwork(probLike=prob_like, probFollow=prob_foll)
        network.loadNetwork(netfile)
        events = [x.rstrip('\n') for x in eventfile]
        return SocialNetworkSimRunner.ExecEventFile(network, events)

    @staticmethod
    def ExecEventFile(network, events) -> DSALinkedList:
        outcome = ""
        from collections import namedtuple
        SimStats = namedtuple('SimStats', ('post simstate likes clustering '
                                           'favg fsd'))
        state = DSALinkedList()
        post = 0
        for x in events:
            tokens = x.split(':')
            if len(tokens) == 3 and tokens[0] == "F":
                network.follow(tokens[2], tokens[1])
            elif len(tokens) == 3 and tokens[0] == "U":
                network.unfollow(tokens[2], tokens[1])
            elif len(tokens) == 2 and tokens[0] == "A":
                try:
                    network.addUser(tokens[1])
                except ValueError as ex:
                    print(str(ex))
            elif len(tokens) == 2 and tokens[0] == "R":
                network.removeUser(tokens[1])
            elif len(tokens) == 3 or len(tokens) == 4 and tokens[0] == "P":
                if len(tokens) == 3:
                    network.addPost(tokens[1], tokens[2])
                else:
                    network.addPost(tokens[1], tokens[2], float(tokens[3]))
                while not network.done():
                    state.insertLast(SimStats(post,
                                              network.simstate(),
                                              network.likesScaled(),
                                              network.clusteringCoefficient(),
                                              *network.followsAvSd()))
                    network.update()
                post += 1
            else:
                raise ValueError("Invalid file format.")
        return state

    @staticmethod
    def GeneratePosts(*, size: int, post_num: int, clickbait_sd: float):
        with NamedTemporaryFile(delete=False, mode='w') as f:
            postFilename = f.name
            for _ in range(post_num):
                postNode = f"A{random.choice(range(size))}"
                f.write(f"P:{postNode}:CONTENT:"
                        f"{max(0, random.gauss(1, clickbait_sd))}\n")
        return postFilename

    @staticmethod
    def GenerateSocialNetwork(*, size: int,
                              follower_av: float,
                              follower_sd: float,
                              clustering_func: Callable[[float], float]
                              ) -> str:
        """
        To generate the simulated networks, a unique algorithm was used
        that was created by the author, and to their knowledge, does not exist
        anywhere else. This algorithm allows efficient generation of
        structured (non-random) networks, with a consistent runtime complexity
        of O(V*E).

        First, a number of verticies are created.
        Next, these verticies are iterated over, and the number of successors
        of each vertex is calculated by sampling from a distribution
        X ~ N(follower_av, follower_sd^2).

        To select the edges of the network, an approach was used that is
        similar in concept to a variogram, used in the field of geostatistics.
        A variogram measures the amount of correlation between two points in
        a field that are some distance apart.
        In this algorithm, this distance is discrete rather than continuous,
        and is measured by finding a path between two nodes.
        By increasing the correlation between nodes at short distances,
        a graph can be created with a higher clustering coefficient.
        Alternatively, decreasing the correlation between nodes causes the
        graph to become more randomised, and less clustered.

        The clustering coefficient of a vertex can be generalized to include
        all verticies within some distance h of a central vertex, rather than
        only verticies within a distance of 1 of the central vertex.

        In a social network, it is reasonable to assume that the clustering
        coefficient will decrease as the distance increases.
        One way to visualise this is that your friends are likely to be
        interconnected, whereas your friends of friends are less likely to be
        interconnected directly. By creating graphs that follow this property,
        realistic social networks can be created for use in simulations.

        To generate an edge in the graph, a random walk is performed starting
        at a given vertex, V_0. This random walk occurs along any nodes that
        are predecessors of the current node, and does not loop back onto
        previously visited nodes.
        At each step on the random walk, the probability of creating an edge
        between the current node and V_0 is calculated by evaluating the
        variogram v(h), where h is the distance that has been travelled
        on the random walk.

        If an edge is created, a new random walk begins starting at the vertex
        $V_0$, and this algorithm repeats until the correct number of edges
        have been created for this vertex.
        If there are no valid verticies to walk to,
        or the random walk has reached some distance threshold from the
        original node, an edge is created with any random vertex in the graph.
        This allows initial 'bootstrapping' of the network when no edges have
        yet been created.
        """
        network = DSADirectedGraph()
        # Add verticies
        for x in range(size):
            # Value is number of followers
            foll_num = int(random.gauss(follower_av, follower_sd))
            network.addVertex(f"A{x}", min(size - 1, max(0, foll_num)))
        # Add edges
        for n in range(size):
            node = network.getVertex(f"A{n}")
            for x in range(node.value):
                # Randomly walk through graph via "followed" connections, with
                # a decreasing chance of following.
                # If an end is reached, or a certain threshold, then a random
                # node is selected to be connected.
                threshold = 5
                walk = DSALinkedList()
                walk.insertLast(node)
                exhausted = False
                done = False
                while len(walk) - 1 < threshold and not exhausted and not done:
                    valid_nodes = list(filter(lambda x: not walk.find(x),
                                              [v for _, v in
                                               walk.peekFirst().predecessor]))
                    if len(valid_nodes) == 0:
                        exhausted = True
                    else:
                        walk.insertFirst(random.choice(valid_nodes))
                        vario = clustering_func(len(walk))
                        label = walk.peekFirst().label
                        will_follow = (numpy.random.binomial(1, vario)
                                       and not node.successor.hasKey(label))
                        if will_follow:
                            done = True
                            network.addEdge(node.label, walk.peekFirst().label)
                # Follow someone random if no-one was
                # followed during the random walk.
                if not done:
                    # Inefficient
                    possibleNodes = [f"A{x}" for x in range(size)]
                    successorLabels = [k for k, _ in node.successor]

                    def filter_func(x):
                        return (x not in successorLabels
                                and x != node.label)
                    possibleNodes = list(filter(filter_func,
                                                possibleNodes))
                    network.addEdge(node.label, random.choice(possibleNodes))
        with NamedTemporaryFile(delete=False, mode='w') as f:
            netFilename = f.name
            f.write(network.displayExploded())
        return netFilename

    @staticmethod
    def GridSearch(stream: Callable[[None], str]):
        """
        To profile multiple runs of the simulation a gridsearch algorithm was
        used to vary the below parameters:
            - Average and s.d. of followers per user
            - Like/Follow probabilities
            - Number of users in the network

        First, arrays that contain the parameter values to be tested are
        created. Next, for all possible combinations of these parameters,
        a network matching these parameters is created. A simulation is then
        run on all networks, with simulation statistics being logged to a file
        in CSV format.

        Parameters that are varied during the gridsearch include the like
        and follow probabilities, network size, clickbait standard deviation,
        and follower average / follower standard deviation.

        An advantage of this algorithm is that it is very simple to implement.
        However, a disadvantage is that it takes a long time to execute when
        there are many input parameters.
        The algorithmic complexity of the gridsearch algorithm
        is O(x^n), where n is the number of parameters that are varied and x
        is the number of datapoints per parameter.
        """
        like_prob = [0.1, 0.2, 0.5]
        foll_prob = [0, 0.4, 0.5]
        size = [50]
        follower_average_mult_sz = [0.2]
        follower_sd_mult_av = [0, 0.5]
        clickbait_sd = [0, 1]
        posts = 50

        def runSim(lp, fp, sz, favg, fsd, csd):
            netfile = (SocialNetworkSimRunner.
                       GenerateSocialNetwork(size=sz,
                                             follower_av=favg * sz,
                                             follower_sd=fsd * favg * sz,
                                             clustering_func=lambda x: 0))
            postfile = SocialNetworkSimRunner.GeneratePosts(size=sz,
                                                            post_num=posts,
                                                            clickbait_sd=csd)
            with open(netfile, 'r') as net, open(postfile, 'r') as event:
                stats = SocialNetworkSimRunner.Simulation(net, event, lp, fp)
            stream(f"\n\nlike_prob:{lp},follow_prob:{fp},size:{sz},"
                   f"follower_average_mult_sz:{favg},"
                   f"follower_sd_mult_av:{fsd},clickbait_sd:{csd}\n")
            stream("post,likes,clustering,favg,fsd\n")
            stream("\n".join([f"{x.post},{x.likes},{x.clustering},"
                              f"{x.favg},{x.fsd}" for x in stats]))

        for lp in like_prob:
            for fp in foll_prob:
                for sz in size:
                    for favg in follower_average_mult_sz:
                        for fsd in follower_sd_mult_av:
                            for csd in clickbait_sd:
                                runSim(lp, fp, sz, favg, fsd, csd)


if __name__ == "__main__":
    with open("../report/test.csv", "w") as f:
        def printAndWrite(x):
            print(x, end='')
            f.write(x)
        try:
            SocialNetworkSimRunner.GridSearch(printAndWrite)
        except KeyboardInterrupt:
            print("")
