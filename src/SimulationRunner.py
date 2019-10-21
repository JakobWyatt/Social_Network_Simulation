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


def gridSearch(stream):
    # Gridsearch on parameters
    # Like prob, follow prob, size, follower average, follower sd, clickbait_sd
    like_prob = [0.2, 0.4, 0.6, 0.8, 1]
    foll_prob = [0.2, 0.4, 0.6, 0.8, 1]
    size = [5, 10, 20, 50]
    follower_average_mult_sz = [0.1, 0.5, 1]
    follower_sd_mult_av = [0, 0.5, 1]
    clickbait_sd = [0]
    posts = 10
    outputCsv = ""
    for lp in like_prob:
        for fp in foll_prob:
            for sz in size:
                for favg in follower_average_mult_sz:
                    for fsd in follower_sd_mult_av:
                        for csd in clickbait_sd:
                            files = generateSocialNetworkAndPost(size=sz, follower_av=favg * sz, follower_sd=fsd * favg * sz,
                                                                 clustering_func=lambda x: 0, post_num=posts, clickbait_sd=csd)
                            with open(files[0], 'r') as net, open(files[1], 'r') as event:
                                _, stats = simulation(net, event, lp, fp)
                            stream(f"\n\nlike_prob:{lp},follow_prob:{fp},size:{sz},follower_average_mult_sz:{favg},follower_sd_mult_av:{fsd},clickbait_sd:{csd}\n")
                            stream("post,likes,clustering,favg,fsd\n")
                            stream("\n".join([f"{x.post},{x.likes},{x.clustering},{x.favg},{x.fsd}" for x in stats]))


if __name__ == "__main__":
    #print(generateSocialNetworkAndPost(size=50, follower_av=10, follower_sd=5,
    #                                                             clustering_func=lambda x: 0, post_num=10, clickbait_sd=1))
    with open("../report/data.csv", "w") as f:
        def printAndWrite(x):
            print(x, end='')
            f.write(x)
        gridSearch(printAndWrite)
