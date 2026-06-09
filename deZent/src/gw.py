
from deZent.src.network.net_node import NetworkNodeID, NetAddr, Message
from deZent.src.network.deZent_node import deZentNetworkNode

addr: NetAddr = NetAddr("10.0.0.x") # TODO get IP from IF
net_op: NetAddr = NetAddr("10.0.0.1") # TODO get GW IP from IF

def msg_cb(node_id: NetworkNodeID, msg: Message) -> None:
    print("msg received")
    # TODO: this cb should be used by deZentGateway or Node

net_node: deZentNetworkNode = deZentNetworkNode(
    addr,
    net_op,
    msg_cb
)

