from dataclasses import dataclass

IPAddr = str
@dataclass(frozen=True) # immutable -> hashable
class NetAddr():
    ip: IPAddr
    port: int

NetworkNodeID = int
@dataclass(frozen=True)
class NetworkNodeIDAddr:
    id: NetworkNodeID
    addr: NetAddr