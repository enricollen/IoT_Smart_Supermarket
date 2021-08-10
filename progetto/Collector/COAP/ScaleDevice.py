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
        self.ip_address = ip_addr
        super.__init__(self)

        
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