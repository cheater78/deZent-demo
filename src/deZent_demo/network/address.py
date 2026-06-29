from dataclasses import dataclass
import random

IPAddr = str
@dataclass(frozen=True) # immutable -> hashable
class NetAddr():
    ip: IPAddr
    port: int

NetworkNodeID = int
def create_network_node_id() -> NetworkNodeID:
    return random.randint(0, pow(2, 64))

@dataclass(frozen=True)
class NetworkNodeIDAddr:
    id: NetworkNodeID
    addr: NetAddr