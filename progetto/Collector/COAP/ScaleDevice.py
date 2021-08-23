from COAP.WeightSensor import WeightSensor
from COAP.RefillSensor import RefillSensor

import logging
logger = logging.getLogger("COAPModule")

from COAP.const import SHELF_SCALE
from Node import Node

class ScaleDevice(Node):
    
    weight_sensor = 0
    refill_sensor = 0   
    linked_price_display = ""
    ip_address = ""

    kind = SHELF_SCALE

    def __init__(self, ip_addr):
        self.weight_sensor = WeightSensor(ip_addr)
        self.refill_sensor = RefillSensor(ip_addr)

        self.node_id = self.weight_sensor.node_id   #both the resources share the same node_id
        self.ip_address = ip_addr
        super().__init__()
        
    def is_multi_resources_node(self):
        return True

    def get_resources_state(self):
        w_sensor_outcome = self.weight_sensor.get_current_state()
        r_sensor_outcome = self.refill_sensor.get_current_state()

        #get_current_state returns -1 OR False in case of error 
        if (not w_sensor_outcome and not r_sensor_outcome) or (w_sensor_outcome == -1 and r_sensor_outcome == -1):
            return False
        else:
            self.update_last_seen()
            return self

    #TO DO:
    #proper interface methods to get or set the state of the resources of the node.
    #those methods should also call update_last_seen method on the Nod

    def bind_price_display(self, price_display_ip):
        if(self.linked_price_display!=""):
            logger.warning("[ScaleDevice: bind_scale_device] Scale Device has already been associated with Price Display")
            return False

        self.linked_price_display = price_display_ip

    def delete(self):
        if isinstance(self.weight_sensor, WeightSensor):
            self.weight_sensor.delete()
            del self.weight_sensor
        if isinstance(self.refill_sensor, RefillSensor):
            self.refill_sensor.delete()
            del self.refill_sensor

    def __del__(self):
        self.delete()