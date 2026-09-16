from datetime import datetime

from deZent_demo.network.address import NetworkNodeID
from deZent_demo.network.abstract_node import AbstractNetworkNode
from deZent_demo.network.topology import CentralizedNode

from deZent_demo.ami.measurement_log import RecordLogEntry, RecordLog
from deZent_demo.ami.smart_meter import SmartMeter
from deZent_demo.ami.smart_meter_profile_distribution import SmartMeterProfileDistributionType, SmartMeterProfileDistribution
from deZent_demo.ami.gateway_profile import GatewayProfileType

from deZent_demo.instrument.instrumentable import *
from deZent_demo.instrument.gateway_instrumentor import *

# TODO: possibly move to network, since SMs could be a separate instance
def gw_create_sms(gw_id: NetworkNodeID, sm_profile_type: SmartMeterProfileDistributionType, n_sm_conn: int) -> dict[NetworkNodeID, SmartMeter]:
    sm_dict: dict[NetworkNodeID, SmartMeter] = {}
    sm_profile_distribution = SmartMeterProfileDistribution.create_sm_profile_distribution(sm_profile_type)

    for sm_id in range(n_sm_conn):
        # TODO: make sm_id random UUID - incr. for dev
        sm_dict[sm_id] = SmartMeter.create_sample_sm_from_profile_distribution(gw_id, sm_id, sm_profile_distribution)
    return sm_dict

class Gateway(Instrumentable, CentralizedNode):

    def __init__(
        self,
        node: AbstractNetworkNode,
        ce_id: NetworkNodeID | None = None,
        gw_profile_type: GatewayProfileType = GatewayProfileType.STANDARD,
        n_sm_conn: int = 0,
        sm_profile_distribution_type: SmartMeterProfileDistributionType = SmartMeterProfileDistributionType.TK,
        instrumentor: Instrumentor = Instrumentor(),
        **kwargs: Any,
    ) -> None:
        
        self.gw_profile_type: GatewayProfileType = gw_profile_type
        self.record_log = RecordLog()

        # TODO: possibly move to network, since SMs could be a separate instance
        self.n_sm_conn: int = n_sm_conn
        self.sm_profile_type: SmartMeterProfileDistributionType = sm_profile_distribution_type
        self.l_sms: dict[NetworkNodeID, SmartMeter] = gw_create_sms(node.id(), sm_profile_distribution_type, n_sm_conn)

        super().__init__(
            instrumentor=instrumentor,
            node=node,
            ce_id=ce_id,
            **kwargs
        )

    '''
        get new measurement for the current time point from sm and add to list
        save values in dictionary for smart meters with measurements and time point
    '''
    def collect_curr_measurement_from_sms(self, curr_time: datetime):
        for sm_id in self.l_sms.keys():
            # get sm instance to request current measurement
            sm: SmartMeter = self.l_sms[sm_id]
            # emulate receiving a measurement record from the sm
            # NOTE: would be a async received and buffered record in the wild, that is now queried and handled
            record: RecordLogEntry = sm.receive_measurement_data_record(curr_time)

            # add measurement to log at GW
            self.record_log.add_record(sm_id, record)
            self._instrument(GWInstrumentEvent.GW_COLLECT_SM_MEASUREMENT,
                curr_time, sm_id, record)
    
    # TODO: centralized publication
    
