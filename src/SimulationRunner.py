from SocialNetworkSim import simulation
from ADT.DSADirectedGraph import *
from ADT.DSALinkedList import *

import random
import math
import numpy
import itertools

# Simulation Runner
# The idea here is that some parameters to be varied will be within the post itself,
# whereas some parameters to be varied will occur when the program is run
# First, a function will be called to generate a network file/event file with some properties
# This will be called multiple times in a "gridsearch" fashion, to find data relating the outputs
# and inputs.

def generateSocialNetworkAndPost(*, size: int, follower_av: float, follower_sd: float,
                          clustering_func, post_num, clickbait_sd) -> str:
    # Clustering coefficient is HARD
    # Algorithm to calculate average local clustering coefficient:
    # 1. Count links between nodes in neighbourhood and divide by possible links in neighbourhood.
    # 2. Do this for all nodes in the network, and divide by the total number of nodes.
    # So how do we generate a network with a given clustering coefficient?

    # Clustering_func imports one number and exports a number between [0, 1] for x = [0, 5]

    # THIS IS HOW WE DO IT
    # SO
    # CREATE NODES
    # SAMPLE BETWEEN NODES TO FIND FOLLOWERS PER NODE
    # Don't add just one edge at a time
    # Sample to find a random node, and add all their followers at once. Maybe follow back, depending on mutuality.
    # Exponential distribution along a random walk of followers.

    # Fuck mutuality

    network = DSADirectedGraph()
    # Add verticies
    for x in range(size):
        # Value is number of followers
        network.addVertex(f"A{x}", max(0, int(random.gauss(follower_av, follower_sd))))
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
                valid_nodes = list(filter(lambda x: not walk.find(x), walk.peekFirst().predecessor))
                if len(valid_nodes) == 0:
                    exhausted = True
                else:
                    walk.insertFirst(random.choice(valid_nodes))
                    if numpy.random.binomial(1, clustering_func(len(walk))) and (not node.successor.find(walk.peekFirst())):
                        done = True
                        network.addEdge(node.label, walk.peekFirst().label)
            # Follow someone random if no-one was followed during the random walk.
            if not done:
                # Inefficient
                possibleNodes = [f"A{x}" for x in range(size)]
                successorLabels = [x.label for x in node.successor]
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


if __name__ == "__main__":
    print(generateSocialNetworkAndPost(size=50, follower_av=25, follower_sd=5, clustering_func=lambda x: 1,
                                post_num=50, clickbait_sd=1))
