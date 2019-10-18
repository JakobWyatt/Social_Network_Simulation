from SocialNetworkSim import simulation

if __name__ == "__main__":
    with open("../example/dark_crystal_net.txt", 'r') as network:
        with open("../example/dark_crystal_e1.txt", 'r') as event:
            simulation(network, event, 1, 1)
