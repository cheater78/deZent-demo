from deZent_demo.network.address import *
from deZent_demo.network.net_stack import *
from deZent_demo.network.net_node import *
from deZent_demo.network.protocol import *

class AbstractNetworkOPModule():

    def __init__(self) -> None:
        pass

    def on_raw_message(self, sender: NetAddr, msg: NetworkMessage) -> None:
        pass

    def on_message(self, sender: NetworkNodeID, msg: NetworkNodeMessage) -> None:
        pass

class NetworkOPNSModule(AbstractNetworkOPModule):

    def __init__(self) -> None:
        self._known_peers_: dict[NetworkNodeID, NetAddr] = { }

    def on_raw_message(self, sender: NetAddr, msg: NetworkMessage) -> None:
        pass
        

class NetworkOP:

    def __init__(self,
                 node: AbstractNetworkNode) -> None:
        self.node: AbstractNetworkNode = node
        self.modules: list[AbstractNetworkOPModule] = []

    def add_module(self, module: AbstractNetworkOPModule) -> None:
        self.modules.append(module)

    def run(self) -> None:
        pass

    def __on_msg__(self, sender: NetworkNodeID, msg: Message) -> None:
        for module in self.modules:
            module.on_message(sender, msg)
