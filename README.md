# Social_Network_Simulation
Python code to implement graph simulation of a social network.

Social networks are modelled as a directed graph of users.

There is only one 'active' post at a time.
A post remains active until it has not been liked during 1 timestep.
A user always likes their own post.

## Algorithm
1. Create the initial network from a network file.
2. If in simulation mode, add any followers in the event file.
3. Repeat the below steps. If in simulation mode, stop when all posts have been simulated. If in interactive mode, stop when the user exits the program.
    1. If there are no active posts, either add the next post in the event file (simulation mode) or prompt the user to enter a post (interactive mode).
    2. If a user has liked a post in the last timestep, each of their followers has a probabilitiy of liking the post. If a user likes a post, they have a probability of liking the original poster. When a user is exposed to a post multiple times, they have a higher probability of liking the post.
    3. If in simulation mode, output the simulation state and statistics. This consists of a graph of the users/followers, and a graph of the current post where nodes are users that have liked the post, and edges are how the user has been exposed to the post. The first item in the adjacency list is the original poster.
    The output of step 4 is also printed.
    4. In interactive mode, when statistics are requested, the following information is provided: posts in order of popularity and people in order of popularity.
    5. In interactive mode, user statistics can also be requested. This shows all the users posts, followers, and following.
    6. Additional statistics may be provided.
