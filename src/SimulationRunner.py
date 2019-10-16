from SocialNetworkSim import simulation

if __name__ == "__main__":
    with open("../example/network_file.txt", 'r') as network:
        with open("../example/event_file.txt", 'r') as event:
            simulation(network, event, 1, 1)
