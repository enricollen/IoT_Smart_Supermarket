from COAP.WeightSensor import WeightSensor
from COAP.RefillSensor import RefillSensor

import logging
logger = logging.getLogger("COAPModule")

from COAP.const import SHELF_SCALE

class ScaleDevice:
    
    weight_sensor = 0
    refill_sensor = 0   
    linked_price_display = ""
    ip_addr = ""

    def __init__(self, ip_addr):
        self.weight_sensor = WeightSensor(ip_addr)
        self.refill_sensor = RefillSensor(ip_addr)
        self.ip_addr = ip_addr

        kind = SHELF_SCALE
    
    def bind_price_display(self, price_display_ip):
        if(self.linked_price_display!=""):
            logger.warning("[ScaleDevice: bind_scale_device] Scale Device has already been associated with Price Display")
            return False

        self.linked_price_display = price_display_ip

    def delete(self):
        self.weight_sensor.delete()
        self.refill_sensor.delete()