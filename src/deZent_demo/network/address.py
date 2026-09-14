import random

NetworkNodeID = int
def create_network_node_id() -> NetworkNodeID:
    return random.randint(0, pow(2, 64))