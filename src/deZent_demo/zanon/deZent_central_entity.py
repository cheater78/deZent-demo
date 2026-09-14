
from deZent_demo.network.address import NetworkNodeID
from deZent_demo.network.abstract_node import AbstractNetworkNode

from deZent_demo.network.protocol import *

class deZentCentralEntity():

    def __init__(self,
                 node: AbstractNetworkNode,) -> None:
        
        self.node: AbstractNetworkNode = node
        self.node.register_msg_cb(self._node_msg_cb_)

    def _node_msg_cb_(self, sender: NetworkNodeID, msg: Message) -> None:
        match msg:
            case MessagePublishRecord() as m:
                print(f"===Publication by GW-{sender}===\n\r{str(m.pub_log)}\n\r=#=Publication by GW-{sender}=#=")
            case _:
                pass

    def id(self) -> NetworkNodeID:
        return self.node.id()